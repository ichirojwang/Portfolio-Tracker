const btnEdit = document.getElementById("btnEdit");
const btnCancel = document.getElementById("btnCancel");
const btnConfirm = document.getElementById("btnConfirm");
const fields = document.querySelectorAll(".form-field");

btnEdit.addEventListener("click", (e) => {
    btnCancel.classList.remove("hidden");
    btnConfirm.classList.remove("hidden");
    btnEdit.classList.add("hidden");
    fields.forEach((field) => {
        field.removeAttribute("readonly");
        field.removeAttribute("disabled");
    });
});

btnCancel.addEventListener("click", (e) => {
    btnCancel.classList.add("hidden");
    btnConfirm.classList.add("hidden");
    btnEdit.classList.remove("hidden");
    fields.forEach((field) => {
        field.setAttribute("readonly", true);
        field.setAttribute("disabled", true);
    });
});

const btnEditYear = document.getElementById("btnEditYear");
const btnCancelYear = document.getElementById("btnCancelYear");
const btnConfirmYear = document.getElementById("btnConfirmYear");
const yearFields = document.querySelectorAll(".form-field-year");

btnEditYear.addEventListener("click", (e) => {
    btnCancelYear.classList.remove("hidden");
    btnConfirmYear.classList.remove("hidden");
    btnEditYear.classList.add("hidden");
    yearFields.forEach((field) => {
        field.removeAttribute("readonly");
        field.removeAttribute("disabled");
    });
});

btnCancelYear.addEventListener("click", (e) => {
    btnCancelYear.classList.add("hidden");
    btnConfirmYear.classList.add("hidden");
    btnEditYear.classList.remove("hidden");
    yearFields.forEach((field) => {
        field.setAttribute("readonly", true);
        field.setAttribute("disabled", true);
    });
});

