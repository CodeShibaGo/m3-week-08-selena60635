import config from "../config.js";

const searchForm = document.querySelector(".search-form");
const searchInput = document.querySelector(".search-input");
const searchBar = document.querySelector(".search-bar");
// youtube-data API金鑰
const API_KEY = config.apiKey;

// 關鍵字
let query;
// 執行搜尋取得資料後，分頁按鈕才需要生成，初始為空
let nextPageToken;
let prevPageToken;
async function runSearch(pageToken) {
  document.querySelector(".results").innerHTML = "";
  const res = await axios.get(config.apiUrl, {
    params: {
      part: "id,snippet",
      q: query,
      maxResults: 5,
      key: API_KEY,
      pageToken: pageToken,
    },
  });
  const data = res.data;
  nextPageToken = data.nextPageToken;
  prevPageToken = data.prevPageToken;
  const html = data.items
    .map((item) => {
      const videoId = item.id.videoId;
      const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
      return `
      <li class="search-item">
        <a href="${videoUrl}" class="video" target="_blank">
         <div class="video-img">
          <img src="${item.snippet.thumbnails.default.url}" alt="${item.snippet.title}">
          </div>
          <div class="video-info">
          <h2>${item.snippet.title}</h2>
          <p>By <span class="text-red">${item.snippet.channelTitle}</span> on <span>${item.snippet.publishedAt}</span></p>   
          <p>${item.snippet.description}</p>
          </div>
        </a>
      </li>
    `;
    })
    .join("");

  document.querySelector(".results").innerHTML = html;

  // 加入按鈕
  const buttons = getBtnHtml();
  document.querySelector("#buttons").innerHTML = buttons;
}

// 取得按鈕的HTML內容
function getBtnHtml() {
  return `
     <div class="button-wrap">
       ${
         prevPageToken
           ? `<button class="paging-btn" onclick="prevPage();">上一頁</button>`
           : ""
       }
       ${
         nextPageToken
           ? `<button class="paging-btn" onclick="nextPage();">下一頁</button>`
           : ""
       }
     </div>
  `;
}

// 點擊下一頁按鈕，將nextPageToken傳入並執行搜尋，pageToken:nextPageToken；搜尋請求內容為搜尋下一頁的內容
window.nextPage = function () {
  runSearch(nextPageToken);
};

// 點擊上一頁按鈕，將prevPageToken傳入並執行搜尋，pageToken:prevPageToken；搜尋請求內容為搜尋上一頁的內容
window.prevPage = function () {
  runSearch(prevPageToken);
};

// 監聽表單提交事件，進行搜尋
searchForm.addEventListener("submit", (e) => {
  // 取消提交預設行為
  e.preventDefault();
  query = searchInput.value;
  runSearch();
});

// search-bar聚焦動態效果
searchInput.addEventListener("focus", () => {
  searchBar.classList.add("focused");
});

searchInput.addEventListener("blur", () => {
  if (searchInput.value === "") {
    searchBar.classList.remove("focused");
  }
});
