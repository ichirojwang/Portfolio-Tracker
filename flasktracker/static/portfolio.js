const forms = document.querySelectorAll(".transaction-form");
forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
        const formQty = form.querySelector(".form-qty");
        const formPrice = form.querySelector(".form-price");
        const formFees = form.querySelector(".form-fees");
        const formDate = form.querySelector(".form-date");
        let qty = parseFloat(formQty.value);
        let price = parseFloat(formPrice.value);
        let fees = parseFloat(formFees.value);
        let date = new Date(formDate.value);
        let today = new Date();

        let isInvalid = false;

        if (isNaN(qty) || qty < 0) {
            formQty.classList.add("is-invalid");
            isInvalid = true;
        } else {
            formQty.classList.remove("is-invalid");
        }

        if (isNaN(price) || price < 0) {
            formPrice.classList.add("is-invalid");
            isInvalid = true;
        } else {
            formPrice.classList.remove("is-invalid");
        }

        if (isNaN(fees) || fees < 0) {
            formFees.classList.add("is-invalid");
            isInvalid = true;
        } else {
            formFees.classList.remove("is-invalid");
        }

        if (date > today) {
            formDate.classList.add("date-invalid");
            isInvalid = true;
        } else {
            formDate.classList.remove("date-invalid");
        }

        if (isInvalid) {
            event.preventDefault();
        }
    });
});

const formDates = document.querySelectorAll(".form-dates");
const setMaxDate = () => {
    let today = new Date();
    let year = today.getFullYear();
    let month = String(today.getMonth() + 1).padStart(2, "0");
    let day = String(today.getDate()).padStart(2, "0");
    let formattedDate = `${year}-${month}-${day}`;

    formDates.forEach((date) => {
        date.setAttribute("max", formattedDate);
    });
}

const modalTicker = document.getElementById("tickerT");
const modalTypeSelect = document.getElementById("typeSelectT");
const transactionBtn = document.getElementById("transactionModalBtn");

transactionBtn.addEventListener("click", (e) => {
    modalTicker.value = ""
    modalTypeSelect.value = "buy";
});

const dropdownBtns = document.querySelectorAll(".btn-dropdown");
dropdownBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        modalTicker.value = btn.getAttribute("data-stock");
        modalTypeSelect.value = btn.getAttribute("data-type");
    });
});

const expandBtns = document.querySelectorAll(".btn-expand");
expandBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        let isExpanded = btn.getAttribute("aria-expanded") === "true";
        let img = btn.querySelector("img");
        let imgExpand = "/static/img/arrows-angle-expand.svg";
        let imgCollapse = "/static/img/arrows-angle-contract.svg";
        img.src = isExpanded ? imgCollapse : imgExpand;

        let span = btn.querySelector("span");
        span.textContent = isExpanded ? "Collapse" : "Expand";
    });
});

const deleteStockBtns = document.querySelectorAll(".btn-delete-stock");
const stockId = document.getElementById("stock_id");
deleteStockBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        stockId.value = btn.getAttribute("data-stock-id");
    });
});

const deleteTransactionBtn = document.querySelectorAll(".btn-delete-transaction");
const tIdDel = document.getElementById("t_id_del");
deleteTransactionBtn.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        tIdDel.value = btn.getAttribute("data-t-id");
    });
});

const editTransactionBtn = document.querySelectorAll(".btn-edit-transaction");
const tIdEdit = document.getElementById("t_id_edit");
const editModalType = document.getElementById("typeSelectE");
const editModalTicker = document.getElementById("tickerE");
const editModalQty = document.getElementById("qtyE");
const editModalPrice = document.getElementById("priceE");
const editModalDate = document.getElementById("dateE");
editTransactionBtn.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        tIdEdit.value = btn.getAttribute("data-t-id");
        editModalType.value = btn.getAttribute("data-t-type");
        editModalTicker.value = btn.getAttribute("data-t-ticker");
        editModalQty.value = btn.getAttribute("data-t-qty");
        editModalPrice.value = btn.getAttribute("data-t-price");
        editModalDate.value = btn.getAttribute("data-t-date");
    });
});


document.addEventListener("DOMContentLoaded", () => {
    setMaxDate();
});