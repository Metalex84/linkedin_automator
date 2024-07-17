/*
 * Copyright (c) 2024 [Alejandro Gonzalez Venegas]
 *
 * Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
 * https://creativecommons.org/licenses/by-nc/4.0/
 */

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
    toggleTextarea();
});