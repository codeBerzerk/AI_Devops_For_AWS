#!/usr/bin/env python3
"""
Інтерактивний CLI для K8s LLM Admin
Дозволяє вводити свої промпти та отримувати streaming відповіді
"""

import sys
import json
import requests
from typing import Optional
import argparse

# Додати корінь проекту в sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings


def stream_diagnose(
    message: str,
    resource_type: Optional[str] = None,
    namespace: str = "default",
    kubectl_output: Optional[str] = None,
    language: str = "uk",
    api_url: str = "http://localhost:8000"
):
    """
    Відправити запит на діагностику з streaming відповіддю
    
    Args:
        message: Повідомлення користувача
        resource_type: Тип ресурсу (pod, service, network, тощо)
        namespace: Kubernetes namespace
        kubectl_output: Вивід kubectl команд (опціонально)
        language: Мова (uk або en)
        api_url: URL API сервера
    """
    url = f"{api_url}/api/diagnose/stream"
    
    payload = {
        "message": message,
        "language": language,
        "namespace": namespace,
    }
    
    if resource_type:
        payload["resource_type"] = resource_type
    
    if kubectl_output:
        payload["kubectl_output"] = kubectl_output
    
    print(f"📤 Відправляю запит до LLM...\n")
    print("=" * 80)
    print("💬 Відповідь LLM:\n")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=300)
        response.raise_for_status()
        
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                # SSE формат: data: {json}\n\n
                if line.startswith(b"data: "):
                    data_str = line[6:].decode('utf-8')  # Прибрати "data: "
                    try:
                        data = json.loads(data_str)
                        chunk = data.get("chunk", "")
                        done = data.get("done", False)
                        
                        if chunk:
                            print(chunk, end="", flush=True)
                            full_response += chunk
                        
                        if done:
                            break
                    
                    except json.JSONDecodeError:
                        continue
        
        print("\n" + "=" * 80)
        print(f"\n✅ Відповідь отримана ({len(full_response)} символів)")
        
        return full_response
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Помилка: Не вдалося підключитися до {url}")
        print("   Переконайтеся що API сервер запущений: python api/main.py")
        sys.exit(1)
    
    except requests.exceptions.Timeout:
        print("❌ Помилка: Час очікування вичерпано")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
        sys.exit(1)


def interactive_mode(api_url: str = "http://localhost:8000"):
    """Інтерактивний режим з циклом питань"""
    print("🤖 K8s LLM Admin - Інтерактивний режим")
    print("=" * 80)
    print("Введіть ваші питання про Kubernetes. Для виходу введіть 'exit' або 'quit'")
    print("=" * 80)
    print()
    
    while True:
        try:
            # Введення повідомлення
            message = input("\n💬 Ваше питання: ").strip()
            
            if not message:
                continue
            
            if message.lower() in ['exit', 'quit', 'q']:
                print("\n👋 До побачення!")
                break
            
            # Опціональні параметри
            resource_type = input("   Тип ресурсу (pod/service/network, Enter для пропуску): ").strip() or None
            namespace = input("   Namespace (Enter для 'default'): ").strip() or "default"
            
            print()
            
            # Відправити запит
            stream_diagnose(
                message=message,
                resource_type=resource_type,
                namespace=namespace,
                language="uk",
                api_url=api_url
            )
        
        except KeyboardInterrupt:
            print("\n\n👋 Перервано користувачем. До побачення!")
            break
        except EOFError:
            print("\n\n👋 До побачення!")
            break


def main():
    """Головна функція CLI"""
    parser = argparse.ArgumentParser(
        description="K8s LLM Admin CLI - Інтерактивна діагностика Kubernetes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:

  # Інтерактивний режим
  python cli.py

  # Одноразовий запит
  python cli.py -m "Мій pod в CrashLoopBackOff, що робити?" -t pod

  # З kubectl output
  python cli.py -m "Проаналізуй цей вивід" --kubectl-output "$(kubectl get pods -n default)"

  # З кастомним API URL
  python cli.py -m "Тест" --api-url http://192.168.1.100:8000
        """
    )
    
    parser.add_argument(
        "-m", "--message",
        help="Повідомлення/питання для LLM"
    )
    
    parser.add_argument(
        "-t", "--resource-type",
        help="Тип ресурсу (pod, service, network, тощо)"
    )
    
    parser.add_argument(
        "-n", "--namespace",
        default="default",
        help="Kubernetes namespace (default: default)"
    )
    
    parser.add_argument(
        "-k", "--kubectl-output",
        help="Вивід kubectl команд для аналізу"
    )
    
    parser.add_argument(
        "-l", "--language",
        choices=["uk", "en"],
        default="uk",
        help="Мова відповіді (default: uk)"
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="URL API сервера (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Запустити інтерактивний режим"
    )
    
    args = parser.parse_args()
    
    # Якщо інтерактивний режим або немає повідомлення
    if args.interactive or not args.message:
        interactive_mode(api_url=args.api_url)
    else:
        # Одноразовий запит
        stream_diagnose(
            message=args.message,
            resource_type=args.resource_type,
            namespace=args.namespace,
            kubectl_output=args.kubectl_output,
            language=args.language,
            api_url=args.api_url
        )


if __name__ == "__main__":
    main()
