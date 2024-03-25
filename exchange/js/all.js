// 用API有提供的rates生成我們的貨幣選項，避免選到API沒有提供的幣值導致計算錯誤
const currencyFrom = document.querySelector("#currency-from");
const currencyTo = document.querySelector("#currency-to");
const amountFrom = document.querySelector("#amount-from");
const amountTo = document.querySelector("#amount-to");
const rate = document.querySelector("#rate");
const swap = document.querySelector("#swap-btn");

// 初始化貨幣選項
async function initRateOpt(rate = "TWD") {
  await fetch(`https://api.exchangerate-api.com/v4/latest/${rate}`)
    .then((res) => res.json())
    .then((data) => {
      Object.keys(data.rates).forEach((item) => {
        if (item === rate) {
          currencyFrom.innerHTML += `<option value=${item} selected>${item}</option>`;
        }
        currencyFrom.innerHTML += `<option value=${item}>${item}</option>`;
      });
      Object.keys(data.rates).forEach((item) => {
        if (item === "USD") {
          currencyTo.innerHTML += `<option value=${item} selected>${item}</option>`;
        }
        currencyTo.innerHTML += `<option value=${item}>${item}</option>`;
      });
    });
  calculate();
}

// 貨幣轉換計算
async function calculate() {
  await fetch(
    `https://api.exchangerate-api.com/v4/latest/${currencyFrom.value}`
  )
    // 轉換ReadableStream物件為json格式
    .then((res) => res.json())
    .then((data) => {
      const rateTo = data.rates[currencyTo.value];
      amountTo.value = (amountFrom.value * rateTo).toFixed(2);
      rate.innerHTML = `1 ${currencyFrom.value} = ${rateTo} ${currencyTo.value}`;
      console.log(rateTo);
      console.log(amountTo.value);
    });
}

// 事件監聽，每次更改都要再計算一次
currencyFrom.addEventListener("change", calculate);
currencyTo.addEventListener("change", calculate);
amountFrom.addEventListener("input", calculate);
amountTo.addEventListener("input", calculate);

// rate交換位置
swap.addEventListener("click", () => {
  [currencyFrom.value, currencyTo.value] = [
    currencyTo.value,
    currencyFrom.value,
  ];
  calculate();
});

initRateOpt();
