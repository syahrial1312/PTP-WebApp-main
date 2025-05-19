allMesin = allMesin.map(am => ({ id: am[0], nama: am[1] }));

function searchMachine(event, inputElement) {
    let suggestion = document.getElementById("suggestion");

    if (!inputElement) {
        console.error("Elemen input nama tidak ditemukan.");
        return;
    }
    let input = inputElement.value.toLowerCase();
    suggestion.innerHTML = "";
    if (input === "") {
        suggestion.style.display = "none";
        return;
    }
    let filteredMesin = allMesin.filter(mesin =>
        mesin.nama?.toLowerCase().includes(input) || mesin.id.toLowerCase().includes(input)
    );
    if (filteredMesin.length === 0) {
        suggestion.style.display = "none";
        return;
    }
    filteredMesin.forEach(mesin => {
        let item = document.createElement("a");
        item.className = "list-group-item list-group-item-action";
        item.innerHTML = `<strong>${mesin.id}</strong> - ${mesin.nama}`;
        item.style.cursor = "pointer";
        item.onclick = () => {
            let inputField = document.querySelector("input[name='mesin']");
            if (inputField) {
                // inputField.value = `${mesin.id} - ${mesin.nama}`;
                inputField.value = `${mesin.id}`;
                suggestion.style.display = "none";
            }
        }
        suggestion.appendChild(item);
    });
    suggestion.style.display = "block";
}