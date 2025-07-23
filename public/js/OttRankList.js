document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("ott-card");
  const jsonPath = "../mj_data/OttRanking.json";

  fetch(jsonPath)
    .then((res) => res.json())
    .then((movies) => {
      const maxItems = 10;
      const categories = ["넷플릭스", "티빙", "디즈니 플러스", "박스오피스"];

      categories.forEach((category) => {
        //카드
        const card = document.createElement("div");
        card.className = "card";

        // 카테고리
        const cardTitle = document.createElement("div"); 
        cardTitle.className = "card-title"; 
        cardTitle.textContent = category;

        //카드 본문 - 영화 목록 컨테이너
        const cardBody = document.createElement("div");
        cardBody.className = "card-body";

        const ul = document.createElement("ul");
        ul.className = "list-unstyled";

        // 영화 리스트 렌더링
        const items = movies[category] || [];
        items.slice(0, maxItems).forEach((movie, index) => {
            //li : 각 영화 항목 하나
            const li = document.createElement("li");
            li.className = "movie-item";
            
            // 순위
            const rankNum = document.createElement("div");
            rankNum.className = "rank";
            rankNum.textContent = `${index + 1}`;
            
            // 포스터
            const posterImg = document.createElement("img");
            posterImg.src = movie["포스터"];
            posterImg.alt = movie["제목"]; //이미지가 없을 경우 대비해 alt에 제목 설정
            
            // 제목 + 장르
            const tityDiv = document.createElement("div");
            tityDiv.className = "text";

            const title = document.createElement("span");
            title.textContent = movie["제목"];
            title.className = "title";
            const type_ = document.createElement("span");
            type_.textContent = movie["장르"];
            type_.className = "type_";

            tityDiv.appendChild(title);
            tityDiv.appendChild(type_);

            li.appendChild(rankNum);
            li.appendChild(posterImg);
            li.appendChild(tityDiv);
            ul.appendChild(li);

            // 클릭 시 기존 검색 함수 실행
          li.addEventListener('click', () => {
            executeSearch(movie["제목"]);
          });
        });
        cardBody.appendChild(ul);

        card.appendChild(cardTitle);
        card.appendChild(cardBody);
        

        container.appendChild(card);
      });
    })
    .catch((err) => {
      console.error("데이터 로딩 실패:", err);
      container.textContent = "데이터를 불러오는 데 실패했습니다.";
    });
});
