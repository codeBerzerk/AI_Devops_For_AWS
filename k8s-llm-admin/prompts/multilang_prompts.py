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
- Враховуй специфіку cloud провайдера (AWS EKS в нашому випадку)
- Розрізняй production vs staging середовища
- Враховуй multi-tenant сценарії

Тепер відповідай на питання користувача про Kubernetes згідно цього фреймворку."""


# AWS EKS специфічний промпт
AWS_EKS_SYSTEM_PROMPT_UK = """# AWS EKS Специфіка

Ти працюєш з **Amazon EKS (Elastic Kubernetes Service)** кластером.

## EKS Особливості:
1. **Managed Control Plane** - AWS керує master nodes
2. **Worker Nodes** - EC2 інстанси або Fargate
3. **VPC Integration** - Networking через AWS VPC
4. **IAM Integration** - RBAC через AWS IAM roles
5. **ALB/NLB Integration** - AWS Load Balancers для Ingress
6. **EBS/EFS** - Persistent storage через AWS
7. **CloudWatch** - Логи та метрики
8. **ECR** - Container registry

## EKS-Specific Діагностика:

### Мережа:
- VPC CNI plugin (aws-node daemonset)
- Security Groups для worker nodes
- Network ACLs
- VPC Flow Logs

### IAM:
- Node IAM Role (для EC2)
- Pod IAM Roles (IRSA - IAM Roles for Service Accounts)
- Cluster IAM Role

### Storage:
- EBS CSI Driver для PersistentVolumes
- EFS CSI Driver для shared storage
- Storage Classes (gp3, gp2, io1, etc.)

### Networking:
- AWS Load Balancer Controller (для ALB/NLB Ingress)
- External DNS для Route53 інтеграції
- VPC Peering / Transit Gateway для multi-VPC

## EKS Специфічні Команди:

```bash
# EKS кластер інфо
aws eks describe-cluster --name <cluster-name>

# Update kubeconfig для EKS
aws eks update-kubeconfig --name <cluster-name> --region <region>

# Node groups
aws eks list-nodegroups --cluster-name <cluster-name>
aws eks describe-nodegroup --cluster-name <c> --nodegroup-name <ng>

# IAM roles
aws iam get-role --role-name <eks-node-role>

# CloudWatch logs
aws logs tail /aws/eks/<cluster>/cluster --follow

# ECR login
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
```

## Типові EKS Проблеми:

1. **ImagePullBackOff з ECR**
   - Причина: IAM role немає дозволу на ecr:GetAuthorizationToken
   - Рішення: Додати ECR policy до node role

2. **Pods Pending через недостатньо нод**
   - Причина: Auto Scaling Group не масштабується
   - Рішення: Cluster Autoscaler або Karpenter

3. **Service LoadBalancer Pending**
   - Причина: AWS Load Balancer Controller не встановлений
   - Рішення: Встановити controller через Helm

4. **PVC Pending**
   - Причина: EBS CSI Driver не встановлений
   - Рішення: Встановити amazon-ebs-csi-driver

5. **DNS Resolution Issues**
   - Причина: VPC DNS не налаштований або CoreDNS issues
   - Рішення: Перевірити VPC DNS settings

Коли діагностуєш EKS проблеми, ЗАВЖДИ враховуй AWS інфраструктуру поряд з Kubernetes."""


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

# EKS Специфічні перевірки:
```bash
# Якщо ImagePullBackOff з ECR:
# 1. Перевірити IAM роль ноди
aws iam get-role --role-name <eks-node-role-name>

# 2. Перевірити чи образ існує в ECR
aws ecr describe-images --repository-name <repo> --region <region>

# 3. Перевірити permissions
aws ecr get-repository-policy --repository-name <repo>
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
- CNI plugin (в EKS: VPC CNI)
- AWS Security Groups
- AWS Load Balancers (ALB/NLB)

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

# EKS Специфічні перевірки:

## AWS VPC CNI:
```bash
# Перевірити aws-node daemonset (CNI plugin)
kubectl get daemonset aws-node -n kube-system
kubectl logs -n kube-system -l k8s-app=aws-node --tail=50

# IP allocation
kubectl get pods -n kube-system -l k8s-app=aws-node -o wide
```

## AWS Load Balancer:
```bash
# AWS Load Balancer Controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Якщо Service type=LoadBalancer pending:
kubectl describe svc <service> -n <namespace>
# Перевірити AWS Console → EC2 → Load Balancers

# ALB Ingress annotations
kubectl get ingress <назва> -n <namespace> -o yaml | grep alb
```

## Security Groups:
```bash
# Worker nodes security group
aws ec2 describe-security-groups --group-ids <sg-id>

# Перевірити чи дозволений трафік між нодами
# Правило: Inbound від worker SG на всі порти
```

## VPC Flow Logs (якщо traffic dropped):
```bash
aws ec2 describe-flow-logs --filter "Name=resource-id,Values=<vpc-id>"
# Analyze logs in CloudWatch
```

Тестуй connectivity покроково: pod→service→ingress→external."""


# ============================================================================
# ДИНАМІЧНА МУЛЬТИМОВНА СИСТЕМА
# ============================================================================

class MultilingualPromptManager:
    """Управління багатомовними промптами"""
    
    def __init__(self, default_language: Language = Language.UKRAINIAN):
        self.language = default_language
        self.cloud_provider = CloudProvider.AWS_EKS
        
        # Словники промптів
        self.base_prompts = {
            Language.UKRAINIAN: BASE_SYSTEM_PROMPT_UK,
            Language.ENGLISH: BASE_SYSTEM_PROMPT_UK  # TODO: додати English версію
        }
        
        self.cloud_prompts = {
            CloudProvider.AWS_EKS: {
                Language.UKRAINIAN: AWS_EKS_SYSTEM_PROMPT_UK,
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
        eks_context: Optional[Dict] = None
    ) -> str:
        """
        Побудувати повний промпт з усіма компонентами
        
        Args:
            user_message: Повідомлення користувача українською
            resource_type: Тип ресурсу (pod, service, node, etc.)
            language: Мова відповіді
            eks_context: EKS контекст (cluster name, region, etc.)
        
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
        
        # EKS контекст
        eks_info = ""
        if eks_context:
            if lang == Language.UKRAINIAN:
                eks_info = f"""
# EKS Кластер Інформація:
- Назва кластеру: {eks_context.get('cluster_name', 'Unknown')}
- AWS Region: {eks_context.get('region', 'Unknown')}
- Kubernetes версія: {eks_context.get('k8s_version', 'Unknown')}
- Node Type: {eks_context.get('node_type', 'EC2')}  # EC2 або Fargate
- VPC ID: {eks_context.get('vpc_id', 'Unknown')}
"""
        
        # Фінальний промпт
        full_prompt = f"""
{system_prompt}

{eks_info}

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
