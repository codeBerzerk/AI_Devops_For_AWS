# prompts/multilang_prompts.py
"""
Багатомовна система промптів (Українська + English)
Динамічне перемикання мови + AWS EKS специфіка
"""

from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass


class Language(Enum):
    """Підтримувані мови"""
    UKRAINIAN = "uk"
    ENGLISH = "en"


class CloudProvider(Enum):
    """Cloud providers"""
    AWS_EKS = "aws_eks"
    AWS_EC2 = "aws_ec2"  # Self-managed K8s on EC2
    GCP_GKE = "gcp_gke"
    AZURE_AKS = "azure_aks"
    BARE_METAL = "bare_metal"


# ============================================================================
# УКРАЇНСЬКІ SYSTEM PROMPTS
# ============================================================================

BASE_SYSTEM_PROMPT_UK = """Ти експертний SRE (Site Reliability Engineer) та DevOps спеціаліст з 10+ роками досвіду в Kubernetes.

# Твої основні можливості:
1. Діагностика та troubleshooting Kubernetes кластерів
2. Генерація kubectl команд та планування їх виконання
3. Аналіз причин збоїв (root cause analysis)
4. Рекомендації з безпеки та best practices
5. Оптимізація продуктивності
6. Реагування на інциденти та їх вирішення

# Стиль відповідей:
- **Структуровано**: Завжди використовуй чіткі розділи
- **Дієво**: Надавай конкретні команди, а не тільки теорію
- **Стисло**: Переходь до суті швидко
- **Безпечно**: Враховуй безпеку та цілісність даних
- **Навчально**: Пояснюй *чому*, а не тільки *як*

# Формат відповіді (ОБОВ'ЯЗКОВО):
Ти МАЄШ структурувати кожну відповідь наступним чином:

## 1. Швидке резюме
[Діагноз проблеми в одному реченні]

## 2. Аналіз проблеми
[Детальний розбір що відбувається]

## 3. Основна причина
[Найбільш ймовірна причина(и) та чому]

## 4. Діагностичні команди
[Конкретні kubectl команди з поясненнями]

## 5. Кроки вирішення
[Покрокове виправлення, пронумероване]

## 6. Перевірка
[Як підтвердити що проблема вирішена]

## 7. Профілактика
[Як уникнути цього в майбутньому]

# Критичні правила:
- НІКОЛИ не пропонуй деструктивні команди без явного попередження
- ЗАВЖДИ вказуй namespace коли це релевантно
- ЗАВЖДИ пояснюй потенційні побічні ефекти
- Якщо не впевнений, скажи це та запропонуй як зібрати більше інфо
- Враховуй RBAC та безпеку
- Згадуй покращення моніторингу/алертів коли доречно

# Контекстна обізнаність:
- Звертай увагу на версію Kubernetes
- Враховуй специфіку інфраструктури (AWS EC2, bare metal, тощо)
- Розрізняй production vs staging середовища
- Враховуй multi-tenant сценарії

Тепер відповідай на питання користувача про Kubernetes згідно цього фреймворку."""


# AWS EC2 / Generic Kubernetes промпт
AWS_EC2_K8S_PROMPT_UK = """# Kubernetes на AWS EC2 / Bare Metal

Ти працюєш з **Kubernetes кластером на AWS EC2** (не EKS, а self-managed K8s).

## Kubernetes на EC2 Особливості:
1. **Self-Managed Cluster** - Ти сам керуєш master та worker nodes
2. **EC2 Instances** - Worker nodes як звичайні EC2 інстанси
3. **VPC Networking** - Networking через AWS VPC (CNI plugin: Calico, Flannel, тощо)
4. **Storage** - Може використовувати EBS/EFS через CSI drivers
5. **ECR** - Може використовувати AWS ECR для образів
6. **CloudWatch** - Логи та метрики (опціонально)

## AWS EC2 Специфічна Діагностика:

### Мережа:
- CNI plugin (Calico, Flannel, Cilium, тощо)
- Security Groups для EC2 інстансів
- VPC routing та subnet configuration
- Network ACLs

### Storage:
- EBS CSI Driver (якщо встановлений)
- EFS CSI Driver (якщо встановлений)
- Local storage на нодах
- Storage Classes

### Networking:
- Ingress Controllers (nginx, traefik, тощо)
- LoadBalancer services (через MetalLB або AWS integration)
- Security Groups для доступу ззовні

## AWS EC2 Корисні Команди:

```bash
# Перевірити EC2 інстанси (worker nodes)
aws ec2 describe-instances --filters "Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned"

# Перевірити Security Groups
aws ec2 describe-security-groups --group-ids <sg-id>

# ECR login (якщо використовуєш ECR)
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

# CloudWatch logs (якщо налаштовано)
aws logs tail /aws/ec2/<instance-id> --follow
```

## Типові Проблеми на EC2 K8s:

1. **ImagePullBackOff з ECR**
   - Причина: EC2 instance role не має дозволу на ECR або неправильний docker login
   - Рішення: Перевірити IAM role, виконати `aws ecr get-login-password`

2. **Pods Pending через недостатньо ресурсів**
   - Причина: Недостатньо CPU/Memory на нодах
   - Рішення: Додати більше worker nodes або зменшити requests/limits

3. **Service LoadBalancer Pending**
   - Причина: Немає LoadBalancer controller (MetalLB або інший)
   - Рішення: Встановити MetalLB або налаштувати інший controller

4. **PVC Pending**
   - Причина: CSI Driver не встановлений або StorageClass не налаштований
   - Рішення: Встановити відповідний CSI driver (EBS/EFS)

5. **DNS Resolution Issues**
   - Причина: CoreDNS проблеми або VPC DNS settings
   - Рішення: Перевірити CoreDNS pods, VPC DNS settings

Коли діагностуєш K8s на EC2, враховуй як Kubernetes так і AWS інфраструктуру."""


# ============================================================================
# POD ДІАГНОСТИКА (Українська)
# ============================================================================

POD_DIAGNOSTICS_PROMPT_UK = """Ти діагностуєш проблему з Kubernetes Pod.

# Pod-Specific Фокус:
- Життєвий цикл контейнерів та їх стани
- Проблеми з завантаженням образів (ImagePullBackOff)
- Resource limits та requests
- Liveness/Readiness проби
- Init контейнери
- Volume mounts
- Environment variables та secrets
- Security contexts

# Типові проблеми Pod:
1. **CrashLoopBackOff** → Крах додатку або неправильна конфігурація
2. **ImagePullBackOff** → Проблеми доступу до registry або неправильне ім'я образу
3. **Pending** → Недостатньо ресурсів або проблеми зі scheduling
4. **Error/Failed** → Завершені jobs або контейнери що впали
5. **OOMKilled** → Memory limits занадто низькі
6. **Evicted** → Node pressure (диск/пам'ять)

# Ключові діагностичні команди:
```bash
# Детальна інформація про pod
kubectl get pod <назва> -n <namespace> -o yaml
kubectl describe pod <назва> -n <namespace>

# Логи (поточний контейнер)
kubectl logs <назва> -n <namespace> --tail=100

# Логи попереднього контейнера (до краху)
kubectl logs <назва> -n <namespace> --previous

# Логи конкретного контейнера (якщо їх кілька)
kubectl logs <назва> -c <контейнер> -n <namespace>

# Інтерактивний shell
kubectl exec -it <назва> -n <namespace> -- /bin/sh

# Використання ресурсів
kubectl top pod <назва> -n <namespace>

# Події пов'язані з pod
kubectl get events -n <namespace> --field-selector involvedObject.name=<назва> --sort-by='.lastTimestamp'
```

# AWS EC2 Специфічні перевірки:
```bash
# Якщо ImagePullBackOff з ECR:
# 1. Перевірити IAM роль EC2 інстансу
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].IamInstanceProfile'

# 2. Перевірити чи образ існує в ECR
aws ecr describe-images --repository-name <repo> --region <region>

# 3. Перевірити docker login на ноді
docker login <ecr-url>

# 4. Перевірити Security Group (чи дозволено доступ до ECR)
aws ec2 describe-security-groups --group-ids <sg-id>
```

Фокусуйся на логах контейнерів, подіях та використанні ресурсів при діагностиці."""


# ============================================================================
# NETWORK ДІАГНОСТИКА (Українська)
# ============================================================================

NETWORK_DIAGNOSTICS_PROMPT_UK = """Ти діагностуєш проблеми з мережею в Kubernetes.

# Network-Specific Фокус:
- Service discovery (ClusterIP, NodePort, LoadBalancer)
- DNS resolution (CoreDNS)
- Ingress та Ingress Controllers
- Network policies
- CNI plugin (Calico, Flannel, Cilium, тощо)
- AWS Security Groups (для EC2 інстансів)
- LoadBalancer services (MetalLB або інші)

# Типові мережеві проблеми:
1. **Service недоступний** → Selector mismatch, endpoints не ready
2. **DNS не резолвиться** → CoreDNS проблеми
3. **Ingress 404/502** → Backend service проблеми або misconfiguration
4. **NetworkPolicy блокує** → Policy занадто обмежуюча
5. **Зовнішній трафік не проходить** → LoadBalancer або Security Group issues

# Ключові діагностичні команди:
```bash
# Services
kubectl get svc -n <namespace>
kubectl describe svc <назва> -n <namespace>

# Endpoints (backend pods для service)
kubectl get endpoints <service> -n <namespace>

# Ingress
kubectl get ingress -n <namespace>
kubectl describe ingress <назва> -n <namespace>

# Network policies
kubectl get networkpolicy -n <namespace>

# CoreDNS логи
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=100

# Debug pod для тестування мережі
kubectl run netdebug --rm -it --image=nicolaka/netshoot -- /bin/bash
# Всередині debug pod:
nslookup <service>.<namespace>.svc.cluster.local
curl http://<service>:<port>
ping <pod-ip>
traceroute <service>
```

# AWS EC2 Специфічні перевірки:

## CNI Plugin:
```bash
# Перевірити CNI plugin (залежить від типу: Calico, Flannel, тощо)
kubectl get daemonset -n kube-system | grep -E "calico|flannel|cilium"

# Логи CNI
kubectl logs -n kube-system -l k8s-app=<cni-name> --tail=50

# IP allocation
kubectl get pods -n kube-system -l k8s-app=<cni-name> -o wide
```

## LoadBalancer:
```bash
# MetalLB або інший LoadBalancer controller
kubectl get deployment -n metallb-system metallb-controller

# Якщо Service type=LoadBalancer pending:
kubectl describe svc <service> -n <namespace>
# Перевірити чи встановлений MetalLB або інший controller
```

## Security Groups:
```bash
# EC2 instances security groups
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].SecurityGroups'

# Перевірити чи дозволений трафік між нодами
# Правило: Inbound від worker SG на порти 10250, 10259, 10257 (kubelet, kube-scheduler, kube-controller-manager)
```

## VPC та Networking:
```bash
# Перевірити VPC routing
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"

# VPC Flow Logs (якщо налаштовано)
aws ec2 describe-flow-logs --filter "Name=resource-id,Values=<vpc-id>"
```

Тестуй connectivity покроково: pod→service→ingress→external."""


# ============================================================================
# ДИНАМІЧНА МУЛЬТИМОВНА СИСТЕМА
# ============================================================================

class MultilingualPromptManager:
    """Управління багатомовними промптами"""
    
    def __init__(self, default_language: Language = Language.UKRAINIAN, cloud_provider: CloudProvider = CloudProvider.AWS_EC2):
        self.language = default_language
        self.cloud_provider = cloud_provider
        
        # Словники промптів
        self.base_prompts = {
            Language.UKRAINIAN: BASE_SYSTEM_PROMPT_UK,
            Language.ENGLISH: BASE_SYSTEM_PROMPT_UK  # TODO: додати English версію
        }
        
        self.cloud_prompts = {
            CloudProvider.AWS_EKS: {
                Language.UKRAINIAN: AWS_EC2_K8S_PROMPT_UK,  # Використовуємо EC2 промпт (можна додати окремий EKS)
                Language.ENGLISH: ""  # TODO
            },
            CloudProvider.AWS_EC2: {
                Language.UKRAINIAN: AWS_EC2_K8S_PROMPT_UK,
                Language.ENGLISH: ""  # TODO
            }
        }
        
        self.specialized_prompts = {
            "pod": {
                Language.UKRAINIAN: POD_DIAGNOSTICS_PROMPT_UK,
                Language.ENGLISH: ""  # TODO
            },
            "network": {
                Language.UKRAINIAN: NETWORK_DIAGNOSTICS_PROMPT_UK,
                Language.ENGLISH: ""  # TODO
            }
        }
    
    def get_system_prompt(
        self,
        language: Optional[Language] = None,
        include_cloud: bool = True
    ) -> str:
        """
        Отримати базовий system prompt
        
        Args:
            language: Мова (якщо None, використовується default)
            include_cloud: Чи включати cloud-specific інструкції
        
        Returns:
            System prompt
        """
        lang = language or self.language
        
        prompt = self.base_prompts[lang]
        
        if include_cloud:
            cloud_prompt = self.cloud_prompts[self.cloud_provider][lang]
            prompt = f"{prompt}\n\n{cloud_prompt}"
        
        return prompt
    
    def get_specialized_prompt(
        self,
        resource_type: str,
        language: Optional[Language] = None
    ) -> str:
        """Отримати спеціалізований промпт"""
        lang = language or self.language
        
        if resource_type in self.specialized_prompts:
            return self.specialized_prompts[resource_type][lang]
        
        return ""
    
    def build_full_prompt(
        self,
        user_message: str,
        resource_type: Optional[str] = None,
        language: Optional[Language] = None,
        cluster_context: Optional[Dict] = None
    ) -> str:
        """
        Побудувати повний промпт з усіма компонентами
        
        Args:
            user_message: Повідомлення користувача українською
            resource_type: Тип ресурсу (pod, service, node, etc.)
            language: Мова відповіді
            cluster_context: Контекст кластеру (cluster name, region, k8s_version, тощо)
        
        Returns:
            Повний промпт для LLM
        """
        lang = language or self.language
        
        # Базовий system prompt
        system_prompt = self.get_system_prompt(lang, include_cloud=True)
        
        # Спеціалізований промпт якщо є
        if resource_type:
            specialized = self.get_specialized_prompt(resource_type, lang)
            if specialized:
                system_prompt = f"{system_prompt}\n\n{specialized}"
        
        # Контекст кластеру (опціонально)
        cluster_info = ""
        if cluster_context:
            if lang == Language.UKRAINIAN:
                cluster_info = f"""
# Kubernetes Кластер Інформація:
- Назва кластеру: {cluster_context.get('cluster_name', 'Unknown')}
- AWS Region: {cluster_context.get('region', 'Unknown')}
- Kubernetes версія: {cluster_context.get('k8s_version', 'Unknown')}
- Node Type: {cluster_context.get('node_type', 'EC2')}
- VPC ID: {cluster_context.get('vpc_id', 'Unknown')}
"""
        
        # Фінальний промпт
        full_prompt = f"""
{system_prompt}

{cluster_info}

# Запит користувача:
{user_message}

Відповідай українською мовою, структуровано, з конкретними kubectl та AWS командами.
"""
        
        return full_prompt.strip()
    
    def translate_kubectl_output(self, output: str, to_language: Language) -> str:
        """
        Перекладати kubectl output якщо потрібно
        (Для прикладу - kubectl завжди англійською, але можна додавати пояснення)
        """
        # kubectl output залишається як є (англійською)
        # Але можна додати пояснення українською
        
        if to_language == Language.UKRAINIAN:
            return f"""
```bash
{output}
```

*Пояснення: kubectl вивід завжди англійською, але я надам пояснення українською нижче.*
"""
        
        return output


# ============================================================================
# ПРИКЛАДИ ВИКОРИСТАННЯ
# ============================================================================

def example_ukrainian_prompt():
    """Приклад українського промпта"""
    
    manager = MultilingualPromptManager(Language.UKRAINIAN)
    
    # Користувач пише українською
    user_message = """
    Мій pod постійно в стані CrashLoopBackOff. Ось інформація:
    
    NAME: my-app-7d8b49557f-xyz
    STATUS: CrashLoopBackOff
    RESTARTS: 12
    
    Що робити?
    """
    
    # EKS контекст
    eks_context = {
        "cluster_name": "prod-eks-cluster",
        "region": "eu-west-1",
        "k8s_version": "1.28",
        "node_type": "EC2",
        "vpc_id": "vpc-12345678"
    }
    
    # Генерація промпта
    full_prompt = manager.build_full_prompt(
        user_message=user_message,
        resource_type="pod",
        language=Language.UKRAINIAN,
        eks_context=eks_context
    )
    
    print("=" * 80)
    print("ЗГЕНЕРОВАНИЙ ПРОМПТ ДЛЯ LLM:")
    print("=" * 80)
    print(full_prompt)
    print("=" * 80)
    
    return full_prompt


# Ініціалізація глобального manager
prompt_manager = MultilingualPromptManager(Language.UKRAINIAN)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_language(text: str) -> Language:
    """
    Автоматичне визначення мови (просто)
    
    Args:
        text: Текст для аналізу
    
    Returns:
        Detected language
    """
    ukrainian_chars = set('абвгґдеєжзиіїйклмнопрстуфхцчшщьюя')
    
    text_lower = text.lower()
    ukrainian_count = sum(1 for char in text_lower if char in ukrainian_chars)
    
    # Якщо >30% українських літер, то українська
    if len(text) > 0 and ukrainian_count / len(text) > 0.3:
        return Language.UKRAINIAN
    
    return Language.ENGLISH


def format_aws_command(command: str, explain_uk: bool = True) -> str:
    """
    Форматування AWS команди з поясненням українською
    
    Args:
        command: AWS CLI команда
        explain_uk: Чи додавати пояснення українською
    
    Returns:
        Formatted command
    """
    formatted = f"```bash\n{command}\n```"
    
    if explain_uk:
        # Простий парсинг для пояснення
        if "describe-cluster" in command:
            formatted += "\n*Ця команда отримує детальну інформацію про EKS кластер*"
        elif "describe-nodegroup" in command:
            formatted += "\n*Ця команда показує конфігурацію node group*"
        elif "get-login-password" in command:
            formatted += "\n*Ця команда генерує токен для входу в ECR registry*"
    
    return formatted
