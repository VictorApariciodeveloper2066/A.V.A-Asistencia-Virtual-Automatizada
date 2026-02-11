# ✅ CHECKLIST DE PRUEBAS - DASHBOARD AVA

## 🔐 AUTENTICACIÓN
- [ ] Login con usuario y contraseña
- [ ] Login con Google OAuth
- [ ] Logout funciona correctamente
- [ ] Redirección a login si no hay sesión

## 📊 DASHBOARD PRINCIPAL

### Sidebar
- [ ] Avatar muestra iniciales correctas
- [ ] Nombre completo se muestra
- [ ] Rol/Carrera se muestra correctamente
- [ ] Botón "Mi Horario" activo (verde)
- [ ] Botón "Historial" funciona
- [ ] Botón "Configuración" funciona
- [ ] Botón "Cerrar Sesión" funciona

### Header
- [ ] Saludo personalizado con nombre
- [ ] Rol se muestra (Profesor o Estudiante de [Carrera])
- [ ] Fecha actual se muestra y actualiza
- [ ] Hora actual se muestra y actualiza cada segundo
- [ ] Formato de hora respeta configuración (12h/24h)
- [ ] Botón de notificaciones visible

### Horario Semanal
- [ ] Se muestran 5 días (Lunes a Viernes)
- [ ] Día actual marcado con "Hoy"
- [ ] Fechas correctas para cada día
- [ ] Materias se muestran en el día correcto

### Tarjetas de Materias
- [ ] Nombre de la materia visible
- [ ] Horario se muestra en formato correcto (12h o 24h según config)
- [ ] Aula se muestra si está asignada
- [ ] Borde verde cuando la clase está activa
- [ ] Punto pulsante verde cuando está activa

## 👨‍🏫 FUNCIONALIDADES PROFESOR

### Cuando la clase está activa:
- [ ] Botón "Generar Código" visible
- [ ] Al hacer clic, genera código de 5 caracteres
- [ ] Código se muestra en contenedor especial
- [ ] Botón "Copiar" funciona
- [ ] Botón "Control de Alumnos" funciona
- [ ] Botón "Ver Historial" funciona

### Editar Aula:
- [ ] Botón de editar ubicación visible
- [ ] Al hacer clic, muestra prompt
- [ ] Permite ingresar nueva aula
- [ ] Actualiza aula en tiempo real
- [ ] Muestra "Sin aula asignada" si está vacío

### Control de Alumnos (/asistencia/<id>):
- [ ] Lista de alumnos inscritos
- [ ] Muestra estado actual (Presente/Ausente/Justificado)
- [ ] Permite cambiar estados
- [ ] Botón "Guardar Historial" funciona
- [ ] Muestra justificativos pendientes

### Ver Historial (/historial/<id>):
- [ ] Lista de sesiones guardadas
- [ ] Muestra código de sesión
- [ ] Muestra fecha y hora
- [ ] Muestra estadísticas (P/J/A)
- [ ] Búsqueda por código funciona
- [ ] Botón "Ver Detalles" funciona

## 👨‍🎓 FUNCIONALIDADES ESTUDIANTE

### Cuando la clase está activa:
- [ ] Campo para ingresar código visible
- [ ] Permite escribir código de 6 dígitos
- [ ] Botón "Validar Asistencia" funciona
- [ ] Muestra mensaje de éxito/error
- [ ] Botón "Cargar Justificativo" funciona

### Cargar Justificativo:
- [ ] Formulario se muestra
- [ ] Permite seleccionar materia
- [ ] Permite seleccionar fecha
- [ ] Permite escribir motivo
- [ ] Permite subir archivo
- [ ] Botón "Enviar" funciona

### Historial Alumno:
- [ ] Muestra sesiones de sus materias
- [ ] Búsqueda por código funciona
- [ ] Botón "Ver Detalles" funciona
- [ ] Muestra su estado en cada sesión

## ⚙️ CONFIGURACIÓN

### Datos Personales:
- [ ] Muestra nombre actual
- [ ] Muestra apellido actual
- [ ] Muestra email actual
- [ ] Muestra cédula (no editable)
- [ ] Muestra carrera (solo estudiantes, no editable)
- [ ] Botón "Guardar Cambios" funciona

### Seguridad:
- [ ] Campo contraseña actual
- [ ] Campo nueva contraseña
- [ ] Campo confirmar contraseña
- [ ] Valida contraseña actual
- [ ] Valida que coincidan las nuevas
- [ ] Botón "Cambiar Contraseña" funciona

### Notificaciones:
- [ ] Toggle visible
- [ ] Estado actual correcto
- [ ] Cambia al hacer clic
- [ ] Guarda preferencia

### Preferencias:
- [ ] Selector de formato de hora
- [ ] Muestra opción actual
- [ ] Cambia al seleccionar
- [ ] Se aplica en dashboard inmediatamente

### Gestionar Cursos:
- [ ] Lista de todas las materias
- [ ] Marca las materias actuales
- [ ] Permite seleccionar/deseleccionar
- [ ] Botón "Actualizar" funciona
- [ ] Texto apropiado según rol (Profesor/Estudiante)

### Eliminar Cuenta:
- [ ] Botón en zona roja
- [ ] Pide confirmación
- [ ] Pide contraseña
- [ ] Elimina cuenta y cierra sesión

## 📈 ESTADÍSTICAS (Footer Dashboard)

- [ ] "Materias Inscritas" muestra número correcto
- [ ] "Clases Asistidas" muestra número correcto
- [ ] Formato "X / Y" correcto

## 🔔 NOTIFICACIONES

- [ ] Solicita permiso al cargar
- [ ] Notifica cuando comienza clase (primeros 5 min)
- [ ] Muestra alerta en pantalla
- [ ] No repite notificación en la misma sesión

## 🎨 DISEÑO Y UX

- [ ] Tema oscuro funciona
- [ ] Colores consistentes (verde #39E079)
- [ ] Responsive en móvil
- [ ] Animaciones suaves
- [ ] Sin errores en consola
- [ ] Favicon se muestra

## 🔗 NAVEGACIÓN

- [ ] Todos los enlaces funcionan
- [ ] Redirecciones correctas
- [ ] Breadcrumbs claros
- [ ] Botón "Atrás" funciona donde aplica

## 📱 RESPONSIVE

- [ ] Dashboard funciona en móvil
- [ ] Sidebar colapsa correctamente
- [ ] Tarjetas se adaptan
- [ ] Formularios usables en móvil

## 🐛 MANEJO DE ERRORES

- [ ] Mensajes de error claros
- [ ] No muestra errores técnicos al usuario
- [ ] Validaciones funcionan
- [ ] Feedback visual en acciones

---

## 📝 NOTAS DE PRUEBA

**Fecha de prueba**: _______________
**Probado por**: _______________
**Navegador**: _______________
**Resolución**: _______________

**Errores encontrados**:
1. 
2. 
3. 

**Sugerencias**:
1. 
2. 
3. 

---

## ✅ RESULTADO FINAL

- [ ] Todas las funcionalidades básicas funcionan
- [ ] Todas las funcionalidades de profesor funcionan
- [ ] Todas las funcionalidades de estudiante funcionan
- [ ] Configuración completa funciona
- [ ] Sin errores críticos
- [ ] Listo para producción
