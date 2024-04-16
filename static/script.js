/**
* Funcion para colapsar o expandir un div con el cuadro de texto de enviar mensajes
*/
document.addEventListener('DOMContentLoaded', function () {
    var selectElement = document.getElementById('opciones');
    var textareaContainer = document.getElementById('speech');

    // Función para mostrar u ocultar el textarea según la opción seleccionada
    function toggleTextarea() {
        if (selectElement.value === '2') {
            textareaContainer.style.display = 'block'; // Muestra
        } else {
            textareaContainer.style.display = 'none'; // Oculta
        }
    }

    // Escucha el evento 'change' en el select para mostrar u ocultar el textarea
    selectElement.addEventListener('change', toggleTextarea);

    // Llama a la función al cargar la página para asegurar que el textarea esté oculto si la opción por defecto no es la tercera
    toggleTextarea();
});

/**
 * Funcion para verificar si el numero de shots es valido antes de iniciar una nueva busqueda
 
 */
function verifyShots() {
    var shots = document.getElementById("numero_shots").value;
    alert(session.get('shots', 0));
    if (shots > session.get('shots', 0)) {
        alert("No tienes suficientes shots disponibles");
        document.getElementById("numero_shots").value = remaining_shots;
    }
}