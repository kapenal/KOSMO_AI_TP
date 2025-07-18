// 오늘 날짜 표시
const today = new Date();
const mm = String(today.getMonth() + 1).padStart(2, '0');
const dd = String(today.getDate()).padStart(2, '0');
const formattedDate = `${mm}.${dd}`;


// 오늘 날짜 출력
document.addEventListener('DOMContentLoaded', () => {
document.getElementById('date-display').textContent = `${formattedDate}`;

});

// 영화 인기 리스트
//   const trendData = [
//     "영화: 인사이드 아웃 2",
//     "영화: 범죄도시 4",
//     "영화: 듄: 파트 2",
//     "드라마: 무빙",
//     "예능: 피지컬: 100 시즌 2"
//   ];

//   const trend_list = document.getElementById('trend-list');
//   trendData.forEach(item => {
//     const li = document.createElement('li');
//     li.textContent = item;
//     trend_list.appendChild(li);
//   });