<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Конфигурация JSON {#json-configuration}

Для загрузки и сохранения самостоятельных JSON-моделей версии 1 установите
`fuzzyroutines[config]`. Функция `LoadModel` читает байты UTF-8 и возвращает
неизменяемые определения шкал, Мамдани или Сугено. `AssembleModel`
связывает готовые объекты с явными ID, а `DumpModel` возвращает канонические
байты. Открытие файлов и запуск вычислений выполняет вызывающий код.
Документы проектов подчиняются отдельному контракту.

Ошибка `ConfigurationError` содержит категорию и указатель JSON по RFC 6901.
Экспорт отклоняет пользовательские вычислители и числа, запись которых привела
бы к потере точности. Валидатор загружается по требованию, поэтому скалярные
вычисления не требуют установки дополнения.

::: fuzzyroutines.configuration
    options:
      members:
        - LoadModel
        - DumpModel
        - AssembleModel
        - ModelConfiguration
        - ScaleDefinition
        - ScaleRepresentatives
        - MamdaniBinding
        - MamdaniCentroid
        - SugenoBinding
        - ConfigurationError
