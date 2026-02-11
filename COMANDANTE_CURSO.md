# Funcionalidad: Comandante de Curso

## Descripción
Un **Comandante de Curso** es un estudiante especial que tiene los mismos permisos que un profesor para gestionar asistencias, pero mantiene su rol de estudiante.

## Características

### 1. Campo en Base de Datos
- **Campo**: `es_comandante` (Boolean, default: False)
- **Tabla**: `user`
- **Script de migración**: `agregar_comandante.py`

### 2. Permisos del Comandante
Un estudiante con `es_comandante = True` puede:
- ✅ Generar códigos de asistencia
- ✅ Ver control de alumnos
- ✅ Actualizar asistencias manualmente
- ✅ Resolver justificativos
- ✅ Guardar historial de asistencias
- ✅ Ver historial completo de materias
- ✅ Editar aulas de las materias
- ✅ Descargar reportes PDF/Excel

### 3. Restricciones
- ❌ Solo profesores pueden asignar/remover comandantes
- ❌ Solo estudiantes pueden ser comandantes (no profesores)
- ✅ Los comandantes siguen siendo estudiantes (pueden marcar su propia asistencia)

## Archivos Modificados

### Backend
1. **models/models.py**
   - Agregado campo `es_comandante` al modelo User

2. **routes/front.py**
   - Modificadas validaciones en: `dashboard()`, `ver_asistencia()`, `ver_justificativos()`, `ver_historial()`, `historial_general()`, `historial_alumno()`, `ver_historial_detalle()`
   - Agregada ruta `/gestionar_comandantes` para profesores

3. **routes/auth.py**
   - Modificadas validaciones en: `generate_code()`, `bulk_attendance()`, `resolver_justificativo()`, `guardar_historial()`, `actualizar_aula()`
   - Agregada ruta `/toggle_comandante/<user_id>` para asignar/remover comandantes

### Frontend
1. **templates/dashboard.html**
   - Botones de profesor visibles para comandantes
   - Badge "Comandante" en header y sidebar
   - Edición de aula disponible para comandantes

2. **templates/gestionar_comandantes.html** (NUEVO)
   - Interfaz para que profesores asignen comandantes
   - Lista de estudiantes por materia
   - Toggle para activar/desactivar comandantes

### Scripts
1. **agregar_comandante.py** (NUEVO)
   - Agrega columna `es_comandante` a la base de datos

## Uso

### Para Profesores

1. **Asignar Comandante**:
   ```
   Ir a: /gestionar_comandantes
   Seleccionar estudiante y hacer clic en "Asignar"
   ```

2. **Remover Comandante**:
   ```
   Ir a: /gestionar_comandantes
   Hacer clic en "Comandante" para desactivar
   ```

### Para Comandantes

1. **Acceso Automático**:
   - Al iniciar sesión, verán las mismas funcionalidades que un profesor
   - Pueden generar códigos, controlar asistencias, etc.
   - Mantienen su rol de estudiante (aparece "Comandante" en su perfil)

## Validación de Permisos

Todas las rutas validan permisos con:
```python
if user.role != 'teacher' and not (user.role == 'student' and user.es_comandante):
    return redirect(url_for('front.index'))
```

## Instalación

1. Ejecutar script de migración:
```bash
python agregar_comandante.py
```

2. Reiniciar servidor Flask

3. Acceder como profesor a `/gestionar_comandantes`

## Notas Técnicas

- Los comandantes NO pueden asignar otros comandantes (solo profesores)
- Los comandantes aparecen con badge especial en el dashboard
- La funcionalidad es completamente retrocompatible
- No afecta a usuarios existentes (default: False)
