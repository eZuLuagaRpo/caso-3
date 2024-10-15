# Caso de Estudio 2: Pruebas de Software

Este proyecto fue realizado por Camilo Herrera-Arcila, M.Sc. Prohibido todo su uso y distribución sin previa autorización del autor. Para solicitar más información, escriba a [camilo.arcila97@gmail.com](mailto:camilo.arcila97@gmail.com) y su propósito es solamente educativo para la Universidad de San Buenaventura - Medellín en el curso de Pruebas de Software.

## Descripción del Proyecto

Este proyecto tiene como objetivo proporcionar una experiencia práctica en la generación y ejecución de pruebas de software unitarias e integración, utilizando Pytest y Allure. Se deberá implementar dobles de prueba, gestionar archivos, y aplicar fixtures para el correcto manejo del entorno de pruebas. Ambos serán integrados dentro del framework Django. **Usuario:** clase, **Contraseña:** clase2024.

## Antes de comenzar

- Instale los requerimientos en su entorno virtual
- Pruebe el aplicativo ejecutando:
  
```bash
python manage.py runserver
```

- Ya estás listo para comenzar.
  
## Actividad a Realizar

1. **Exploración del aplicativo**: Como nota, este trabajo no tiene una descripción detallada de la funcionalidad del mismo. Debe explorar el aplicativo para conocer la funcionalidad del software entregado.
2. Se requiere que implementes un análisis predictivo para evaluar la conveniencia de comprar o vender acciones, basándote en los precios de cierre de la bolsa de la marca seleccionada. Deberás desarrollar la función `analyze_data(prices)` (ya la función está creada y conectada con el front, debes desarrollar el contenido de la misma), la cual debe realizar un análisis exhaustivo del comportamiento de los precios a lo largo del periodo indicado. Esta función no solo debe ser robusta y eficiente, sino que también debe reflejar tu comprensión profunda en analítica de datos, dado que se trata de estudiantes de Ingeniería de Datos y Software, así como tu habilidad en pruebas de software. El resultado esperado es un informe detallado que incluya un análisis cuantitativo con un mínimo de 150 palabras, en el cual se informe al usuario sobre la recomendación de compra o venta de acciones, fundamentada en el comportamiento histórico de los precios de cierre. Asegúrate de utilizar técnicas analíticas adecuadas y presentar los resultados de manera clara y comprensible. El resultado del informe se debe mostrar en el front.
3. **Generación de Pruebas**:
   Según su exploración y análisis, realice:
   - Crear pruebas unitarias y de integración del sistema (incluyendo testeo web de respuestas http con REST APIs).
   - Almacenar todas las pruebas en el archivo `tests.py`.
   - Ejecutar las pruebas utilizando Pytest e integrarlo con Django.
4. **Aplicación de Dobles de Prueba**:
   - Implementar dobles de prueba donde sea necesario.
5. **Gestión de Archivos**:
   - Utilizar `tmp_path` y `tmp_path_factory` para la gestión de archivos temporales en las pruebas.
6. **Uso de Fixtures**:
   - Aplicar fixtures para la configuración y limpieza de pruebas (`setUp` y `tearDown`).
7. **Informe Escrito**:
   - Elaborar un informe escrito que contenga:
     - Introducción
     - Resumen ejecutivo con el resultado de todas las pruebas.
     - Sección detallada por cada prueba con:
       - Precondiciones
       - Procesos
       - Post-condiciones
       - Resultado (pasó/no pasó)
       - Recomendación de solución en caso de no pasar.
       - Solución implementada.

8. **Informe Digital con Allure**:
   - Utilizar Allure para generar un informe digital.
   - Incluir metadatos en cada prueba utilizando decoradores de Allure como `@allure.title`, `@allure.issue`, y todas las demás vistas en clase (consulte la página web de allure para más detalles).

### Comandos para Generar el Informe con Allure

Para generar el informe con Allure, utiliza los siguientes comandos:

```bash
# Ejecutar las pruebas y generar el reporte
pytest --alluredir allure-results

# Generar el informe visual
allure generate allure-report
```

## Entregables

Los entregables para esta actividad son:

1. Informe escrito en formato PDF o Word.
2. Informe de Allure generado.
3. Proyecto comprimido en formato ZIP que incluya todas las pruebas en el archivo `tests.py` de Django en la app objetivo.

### Fecha Límite de Entrega

La fecha límite para la entrega de todos los documentos es el domingo 27 de octubre a media noche, en la carpeta `/Entregas/Caso3/apellido_nombre_psoft_caso3.zip`.

## Rúbricas de Evaluación

La evaluación se realizará con base en los siguientes criterios:

1. **Calidad de las Pruebas (40%):** Cobertura de casos de prueba. Uso adecuado de dobles de prueba. Aplicación de fixtures.

2. **Informe Escrito (40%):** Claridad y estructura del informe. Detalle de las pruebas y resultados.

3. **Informe de Allure (20%):** Complejidad de las pruebas, uso adecuado de metadatos que se muestran en el informe html y corercta integración con Django.

¡Buena suerte con el caso de estudio! Si tienen alguna pregunta, no duden en preguntar.
