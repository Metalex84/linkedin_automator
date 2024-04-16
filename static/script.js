function verifyShots() {
    var shots = document.getElementById("numero_shots").value;
    alert(session.get('shots', 0));
    if (shots > session.get('shots', 0)) {
        alert("No tienes suficientes shots disponibles");
        document.getElementById("numero_shots").value = remaining_shots;
    }
}