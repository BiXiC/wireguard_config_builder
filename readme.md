**wg_conf_buider** - утилита для создания конфигурационного файла для wireguard.

**hm_parsing** - утилита для сбора множества ip адресов заданных ресурсов

Собирает актуальный список IP-исключений с сайта https://community.antifilter.download/ и объединяет с любым внешним json файлом, содержащим IP выбранных сайтов.

В переменных окружения должны быть сохранены Socket VPN сервера и его публичный ключ.

**Применение**: 

`python3 wg_conf_builder.py -u USER_NAME -ip VPN_NETWORK_USER_IP_ADDRESS -pk VPN_USER_PRIVATE_KEY`

`USER_NAME` - имя пользователя, для которого создаем конфиг

`VPN_NETWORK_USER_IP_ADDRESS` - IP, выдаваемый пользователю

`VPN_USER_PRIVATE_KEY` - секретный ключ пользователя
