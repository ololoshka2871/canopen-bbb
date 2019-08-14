# Включить CAN1 на BeagleboneBlack

## Pins
Согласно

![картинке](https://i.stack.imgur.com/paWjJ.jpg)

Дополнительные пины управления микросхемой TJA1055:
* STB -> P9.12  (GPIO 60)
* EN ->  P9.14  (GPIO 50)
* WAKE -> P9.16 (GPIO 51)

## Сборка
```sh
sudo ./dtc.sh
```

## Запуск
После перезагрузки 1 раз выполнить
```sh
sudo ./setup.sh
```
