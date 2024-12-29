const stocks = document.querySelectorAll(".stock");
const numChildren = stocks.length;
const speed = Math.min(numChildren * 3, 25);
const delay = "calc( -1s * " + speed + " / " + numChildren + " * (" + numChildren + " - var(--n)))";

const aStock = document.querySelector(".stock");
const stockWidth = parseInt(getComputedStyle(aStock).width);
const stockSlider = document.getElementById("stock-slider");
const sliderMaxWidth = Math.max(stockWidth * numChildren, 1000);
stockSlider.style.setProperty("max-width", sliderMaxWidth + "px");

const descAndLogo = document.querySelector(".desc-and-logo");
descAndLogo.style.setProperty("max-width", sliderMaxWidth + "px");

stocks.forEach(setProperties);

function setProperties(stock, index) {
    stock.style.setProperty("left", "max(120%, " + (sliderMaxWidth - 100) + "px)")
    stock.style.setProperty("--n", index + 1);
    stock.style.setProperty("animation-duration", speed + "s");
    stock.style.setProperty("animation-delay", delay);

    var movement = stock.querySelector(".movement");
    var percentDiv = stock.querySelector(".percent");
    var amountDiv = stock.querySelector(".amount");

    var percent = parseFloat(percentDiv.textContent);
    var amount = parseFloat(amountDiv.textContent);
    var arrow = stock.querySelector(".arrow");

    if (percent > 0) {
        arrow.classList.add("up");
        movement.style.setProperty("background-color", "var(--lightgreen)")
        movement.style.setProperty("color", "var(--green)")
        amountDiv.classList.add("pos");
    } else if (percent < 0) {
        arrow.classList.add("down");
        movement.style.setProperty("background-color", "var(--lightred)")
        movement.style.setProperty("color", "var(--red)")
        amountDiv.textContent = Math.abs(amount).toFixed(2);
        amountDiv.classList.add("neg");
    }
}



