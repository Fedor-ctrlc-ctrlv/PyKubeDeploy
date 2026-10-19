**PyKubeDeploy** — пет-проект для автоматизированного развёртывания односерверного Kubernetes-кластера и PostgreSQL на виртуальной машине Ubuntu Server.

Развёртывание запускается из Python CLI в WSL. CLI передаёт параметры Ansible, который подключается к виртуальной машине по SSH, устанавливает k3s и создаёт ресурсы PostgreSQL в Kubernetes.

Цель проекта — отработать на практике настройку Linux-сервера, сетевое взаимодействие между хостом и виртуальной машиной, SSH, Ansible, Kubernetes, хранение данных и диагностику проблем инфраструктуры.

## Архитектура

```text
Windows 10
└── WSL (Ubuntu)
    └── Python CLI
        └── Ansible (SSH)
            └── Ubuntu Server 26.04 LTS (VirtualBox)
                └── k3s (одна control-plane нода)
                    └── namespace: database
                        ├── PostgreSQL 17 (StatefulSet)
                        ├── Service: postgres (headless)
                        ├── Secret: postgres-secret
                        └── PVC: 3 GiB (local-path)
```

В проекте используется один сервер. Это лабораторная конфигурация, а не отказоустойчивый кластер.

## Используемые технологии

| Технология | Назначение |
| --- | --- |
| Python | CLI для запуска развёртывания и ввода параметров |
| Ansible | Автоматизация настройки сервера и ресурсов Kubernetes |
| SSH | Удалённое подключение к Ubuntu Server |
| VirtualBox | Виртуализация сервера |
| Ubuntu Server 26.04 LTS | Операционная система сервера |
| k3s | Лёгкий дистрибутив Kubernetes |
| Kubernetes | Управление контейнеризированными сервисами |
| PostgreSQL 17 | Реляционная база данных |
| Bash, systemd, systemd-resolved | Диагностика и возможная автоматизация настройки DNS |
| WSL | Среда запуска Python и Ansible на Windows |

## Как работает развёртывание

1. Пользователь запускает `python3 cli/main.py` в WSL.
2. CLI запрашивает IP сервера, SSH-порт, SSH-пользователя и пароль PostgreSQL.
3. Пароль PostgreSQL временно передаётся Ansible через JSON-файл с ограниченными правами доступа; после завершения CLI удаляет этот файл.
4. Ansible подключается к серверу по SSH и повышает привилегии через `sudo`.
5. Роль `k3s` проверяет наличие установки, при необходимости скачивает и запускает установщик, проверяет сервис и ожидает готовности Kubernetes-ноды.
6. Роль `postgres` формирует Kubernetes-манифест, применяет его и ожидает готовности StatefulSet.
7. CLI выводит результат выполнения Ansible.

Запуск из корня проекта:

```bash
python3 cli/main.py
```
Для SSH и `sudo` в текущем варианте используются запросы паролей Ansible (`--ask-pass`, `--ask-become-pass`).

## Развёртывание PostgreSQL

PostgreSQL разворачивается в namespace `database`:

- **StatefulSet** с одной репликой и образом `postgres:17`;
- **Secret** `postgres-secret` для пароля пользователя БД;
- **Headless Service** `postgres` на порту `5432`;
- **PersistentVolumeClaim** на `3Gi` с StorageClass `local-path`;
- база `appdb` и пользователь `appuser`.
Внутри Kubernetes сервис доступен по DNS-имени `postgres.database.svc.cluster.local` на порту `5432`.

## Автоматизация настройки DNS с помощью Bash и systemd
```bash
resolvectl status
getent hosts get.k3s.io
```

На NAT-интерфейсе `enp0s3` использовался DNS-сервер `192.168.1.1`, который в данной конфигурации не обеспечивал корректное разрешение имён.

**Временное решение:**

```bash
sudo resolvectl dns enp0s3 1.1.1.1 8.8.8.8
sudo resolvectl domain enp0s3 '~.'
```

После изменения DNS команда `getent hosts get.k3s.io` начала возвращать адреса, и установщик k3s удалось скачать.
Для автоматизации этого решения был написан Bash-скрипт pykubedeploy-dns.sh. Для автоматического выполнения скрипта при запуске Ubuntu Server был создан собственный systemd-юнит pykubedeploy-dns.service. Сервис был добавлен в автозагрузку и запущен, после перезагрузки виртуальной машины была проверена работоспособность DNS - скрипт успешно выполняется при старте системы, а разрешение доменных имён продолжает работать.
