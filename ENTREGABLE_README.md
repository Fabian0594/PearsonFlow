# 📄 Entregable PearsonFlow - Documentación LaTeX

## 🎯 Descripción

Este directorio contiene el entregable completo del proyecto **PearsonFlow** para la materia de Programación Orientada a Objetos. El documento está elaborado en LaTeX y cumple con todos los requisitos especificados en el enunciado del proyecto.

## 📋 Contenido del Entregable

### 📄 Documento Principal: `entregable_pearsonflow.tex`

El documento LaTeX incluye todas las secciones requeridas:

1. **Portada** - Información del proyecto y estudiante
2. **Introducción y Contexto** - Temática y justificación del sistema
3. **Requerimientos del Sistema** - Funcionales y no funcionales
4. **Librerías Implementadas** - Tecnologías y frameworks utilizados
5. **Flujo de Trabajo** - Arquitectura y proceso de ejecución
6. **Conceptos POO** - Implementación de clases, herencia, polimorfismo, etc.
7. **Patrón de Diseño** - Factory Method implementado
8. **Tarjetas CRC** - Clase-Responsabilidad-Colaboración
9. **Diagrama de Clases** - Representación UML del sistema
10. **Casos de Uso** - Diagramas y especificaciones detalladas
11. **Interfaces Gráficas** - Descripción de las 4 interfaces implementadas
12. **Estructura del Código** - Organización y métricas
13. **Seguridad** - Sistema de gestión de credenciales
14. **Pruebas y Validación** - Scripts de testing
15. **Conclusiones** - Logros y aprendizajes
16. **Referencias** - Bibliografía utilizada

## 🛠️ Cómo Compilar el Documento

### Opción 1: Overleaf (Recomendado)

1. Ve a [Overleaf](https://www.overleaf.com/)
2. Crea una cuenta o inicia sesión
3. Crea un nuevo proyecto
4. Copia el contenido de `entregable_pearsonflow.tex`
5. Pégalo en el editor de Overleaf
6. El documento se compilará automáticamente

### Opción 2: LaTeX Local

Si tienes LaTeX instalado localmente:

```bash
# Compilar el documento
pdflatex entregable_pearsonflow.tex

# Si hay referencias cruzadas, ejecutar dos veces
pdflatex entregable_pearsonflow.tex
pdflatex entregable_pearsonflow.tex
```

### Opción 3: Docker con LaTeX

```bash
# Usar contenedor Docker con LaTeX
docker run --rm -v $(pwd):/workspace -w /workspace texlive/texlive:latest pdflatex entregable_pearsonflow.tex
```

## 📦 Paquetes LaTeX Requeridos

El documento utiliza los siguientes paquetes (incluidos en distribuciones completas de LaTeX):

- `babel` - Soporte para español
- `geometry` - Configuración de márgenes
- `graphicx` - Inclusión de imágenes
- `listings` - Código fuente con sintaxis
- `xcolor` - Colores personalizados
- `hyperref` - Enlaces y referencias
- `tikz` - Diagramas y gráficos
- `pgf-umlcd` - Diagramas UML
- `longtable` - Tablas largas
- `booktabs` - Tablas profesionales

## 🖼️ Recursos Adicionales Necesarios

### Imagen del Logo (Opcional)
El documento hace referencia a `logo_universidad.png`. Puedes:

1. **Agregar tu logo universitario** - Coloca el archivo en el mismo directorio
2. **Comentar la línea** - Si no tienes logo, comenta esta línea:
   ```latex
   % \includegraphics[width=0.3\textwidth]{logo_universidad.png}\\[1cm]
   ```

### Información Personal
Actualiza estos campos en la portada:

```latex
\textbf{Integrante:} & Fabián Hurtado \\
\textbf{Código:} & [Tu código estudiantil] \\
\textbf{Profesor:} & [Nombre del profesor] \\
\textbf{Universidad:} & [Nombre de la universidad] \\
```

## 📊 Características del Documento

### ✅ Cumplimiento de Requisitos

- **✅ Clases y Objetos** - 18 clases implementadas
- **✅ Herencia** - Jerarquías DataLoader, Chart, AIModel
- **✅ Polimorfismo** - Interfaces comunes implementadas
- **✅ Encapsulamiento** - Atributos privados y métodos controlados
- **✅ Modularidad** - Organización en módulos especializados
- **✅ Patrón de Diseño** - Factory Method implementado
- **✅ 4+ Interfaces Gráficas** - LoadWindow, DataVisualizerGUI, AI Panel, Notebook
- **✅ Implementación en Python** - Todo el código en Python 3.x

### 📈 Métricas del Proyecto

- **4,529 líneas de código**
- **18 clases principales**
- **113 métodos implementados**
- **4 interfaces gráficas**
- **3 modelos de IA integrados**
- **Sistema de seguridad completo**

## 🎨 Características del Documento LaTeX

### Diseño Profesional
- Portada elegante con información del proyecto
- Tabla de contenidos automática
- Numeración de páginas y encabezados
- Código fuente con resaltado de sintaxis
- Diagramas UML profesionales
- Tablas y figuras bien formateadas

### Estructura Académica
- Formato estándar para documentos académicos
- Referencias bibliográficas apropiadas
- Secciones organizadas lógicamente
- Especificaciones técnicas detalladas
- Análisis completo del sistema

## 🚀 Uso del Documento

### Para Estudiantes
1. **Personaliza** la información en la portada
2. **Revisa** que todos los conceptos POO estén claros
3. **Compila** el documento en Overleaf
4. **Descarga** el PDF final para entrega

### Para Profesores
- Documento completo que demuestra dominio de POO
- Implementación real de patrones de diseño
- Sistema funcional con interfaces gráficas
- Análisis técnico detallado
- Código fuente bien documentado

## 📝 Notas Importantes

1. **Código Fuente Incluido** - El proyecto completo está en el repositorio
2. **Sistema Funcional** - PearsonFlow es un sistema completamente operativo
3. **Documentación Completa** - README.md y SECURITY.md incluidos
4. **Seguridad Implementada** - Sistema de credenciales seguras
5. **Pruebas Incluidas** - Scripts de testing y validación

## 🔗 Enlaces Útiles

- [Overleaf](https://www.overleaf.com/) - Editor LaTeX online
- [LaTeX Tutorial](https://www.latex-tutorial.com/) - Guía de LaTeX
- [TikZ Examples](https://texample.net/tikz/) - Ejemplos de diagramas
- [LaTeX Symbols](https://oeis.org/wiki/List_of_LaTeX_symbols) - Símbolos LaTeX

## 📞 Soporte

Si tienes problemas compilando el documento:

1. **Verifica** que todos los paquetes estén instalados
2. **Usa Overleaf** para evitar problemas de configuración
3. **Comenta** las líneas problemáticas temporalmente
4. **Consulta** la documentación de LaTeX

---
