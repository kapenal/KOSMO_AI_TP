// 페이지 로드 시 진행
window.addEventListener('DOMContentLoaded', () => {
  const parts = window.location.pathname.split('/');
  const movieId = parts[parts.length - 1];
  const params = new URLSearchParams(window.location.search);
  const title = params.get('title') || '';
  loadRecommendations(title);  // 추천 영화
  loadMovieDetail(movieId);   // 영화 상세 정보
  loadReviews(movieId);       // 리뷰 출력
  loadReviewWordBubbleChart(movieId); // 리뷰 단어 버블 차트`
});

// 영화 상세 데이터 함수
function loadMovieDetail(movieId) {
  fetch(`/api/movie/${movieId}`)
    .then(res => res.json())
    .then(movie => {
      document.getElementById('title_ko').textContent = `${movie.제목}`;
      document.getElementById('release_date').textContent = `${movie.연도}`;
      document.getElementById('rating_value').textContent = `${movie.평점}`;
      document.getElementById('overview').textContent = movie.줄거리 || '줄거리 정보가 없습니다.';
      document.getElementById('genres').textContent = movie.장르.join(', ');

      if (movie.포스터) {
        const posterImg = document.getElementById('poster');
        posterImg.src = movie.포스터;
        posterImg.classList.remove('d-none');
        document.getElementById('poster_empty').classList.add('d-none');
      }
    })
    .catch(err => {
      console.error('영화 상세 불러오기 실패:', err);
      document.getElementById('overview').textContent = '영화 정보를 불러올 수 없습니다.';
    });
}

// 리뷰 데이터 함수
function loadReviews(movieId) {
  fetch(`/api/review/${movieId}`)
    .then(res => res.json())
    .then(data => {
      const reviewContainer = document.getElementById('review_list');
      reviewContainer.innerHTML = ''; // 기존 리뷰 지우기

      // data 자체가 배열이므로 data.forEach 사용
      data.forEach(review => {
        const div = document.createElement('div');
        div.className = 'review-item';
        div.innerHTML = `
          <p class="review-nickname"><strong>${review.닉네임}</strong></p>
          <p class="review-text">${review.리뷰}</p>
          <p class="review-score">평점: ${review.평점}</p>
        `;
        reviewContainer.appendChild(div);
      });
      if(data.length === 0) {
        reviewContainer.innerHTML = '<p>현재 리뷰가 없습니다.</p>';
      }
    })
    .catch(err => {
      console.error('리뷰 불러오기 실패:', err);
    });
}

// 추천 영화 리스트 생성 함수
function loadRecommendations(title) {
  fetch(`/api/recommend?title=${encodeURIComponent(title)}`)
    .then(res => res.json())
    .then(recommendData => {
      const container = document.getElementById('recommend_list');
      container.innerHTML = '';
      const spinner = document.getElementById('loading-spinner');

      recommendData.recommendations.forEach(movie => {
        const movieDiv = document.createElement('div');
        movieDiv.className = 'recommend-item bg-secondary';
        movieDiv.style.cssText = "width: 220px; height: 350px; text-align: center; padding: 10px; box-sizing: border-box; cursor: pointer;";

        movieDiv.innerHTML = `
          <img src="${movie.poster_path ? movie.poster_path : '/img/unimg.jpg'}" 
          onerror="this.onerror=null; this.src='/img/unimg.jpg';"
          style="width: 150px; height: 250px;" 
          alt="${movie.title_ko}">
          <p><strong></strong> ${movie.title_ko}</p>
          <p><strong></strong> ${(movie.genres || []).slice(0, 2).join(', ')}</p>
        `;

        // 클릭 시 기존 검색 함수 실행
        movieDiv.addEventListener('click', () => {
          executeSearch(movie.title_ko);
        });

        container.appendChild(movieDiv);
      });
    })
    .catch(err => {
      console.error("추천 영화 불러오기 실패:", err);
    });
}

// 리뷰 단어 버블 차트 함수
function loadReviewWordBubbleChart(movieId) {
  const spinner = document.getElementById('loading-spinner');
  
  // 로딩 스피너 표시
  spinner.style.display = 'block';
  
  fetch(`/api/wordbubble/${movieId}`)  // 단어 빈도 API 경로에 맞게 변경하세요
    .then(res => res.json())
    .then(data => {
      spinner.style.display = 'none';

      // data가 배열인지, 그리고 비어있지 않은지 확인
      if (!Array.isArray(data) || data.length === 0) {
        console.warn('데이터가 없거나 올바른 배열 형식이 아닙니다.');
        document.getElementById('word-bubble-chart').innerHTML = '<text x="20%" y="50%">리뷰 단어 버블 차트를 불러올 수 없습니다.</text>';  
        return;  // 데이터가 없으면 차트 그리지 않음
      }

      // console.log('버블 차트 데이터:', data);  // 디버깅용 로그

      const svg = d3.select('#word-bubble-chart');
      svg.selectAll('*').remove(); // 기존 차트 지우기

      const width = +svg.attr('width');
      const height = +svg.attr('height');

      // 파스텔 톤 색상 정의 (파스텔 색상 배열)
      const pastelColors = [
        "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", 
        "#FFB6C1", "#FFCCCB", "#E0BBE4", "#D4F1F4", "#FFABAB"
      ];
      const color = d3.scaleOrdinal(pastelColors);

      // 크기 스케일 설정
      const sizeScale = d3.scaleSqrt()
        .domain([d3.min(data, d => d.value), d3.max(data, d => d.value)])
        .range([20, 80]);

      const root = d3.pack()
        .size([width, height])
        .padding(5)(d3.hierarchy({ children: data }).sum(d => d.value));

      const node = svg.selectAll('g')
        .data(root.leaves())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x},${d.y})`);

      // 원 추가
      const circles = node.append('circle')
        .attr('r', d => d.r)
        .attr('fill', (d, i) => color(i))
        .on('mouseover', function (event, d) {
          // 호버 시 원과 텍스트 크기 모두 증가
          d3.select(this).transition().duration(300).attr('r', d.r * 1.5);  // 원 크기 증가
          d3.select(this.nextElementSibling)  // 텍스트 크기 증가
            .transition().duration(300)
            .style('font-size', `${Math.min(2 * (d.r * 1.5) / d.data.text.length, 25)}px`);
        })
        .on('mouseout', function (event, d) {
          // 호버 해제 시 원과 텍스트 크기 원래대로 복구
          d3.select(this).transition().duration(300).attr('r', d.r);  // 원 크기 복구
          d3.select(this.nextElementSibling)  // 텍스트 크기 복구
            .transition().duration(300)
            .style('font-size', `${Math.min(2 * d.r / d.data.text.length, 20)}px`);
        });

      // 텍스트 추가 (글자 크기도 호버 시 커짐)
      node.append('text')
        .attr('class', 'bubble-text')
        .text(d => d.data.text)
        .style('font-size', d => Math.min(2 * d.r / d.data.text.length, 25) + 'px')
        .attr('dy', '.3em')
        .attr('text-anchor', 'middle')
        .style('pointer-events', 'none');  // 텍스트에 마우스 이벤트를 전달하지 않음
    })
    .catch(err => {
      console.error('단어 버블 차트 데이터 로드 실패:', err);
    });
}
// 추가사항(리뷰 구현)
function submitReview() {
  const reviewText = document.getElementById('review_text').value.trim();
  const score = document.getElementById('review_score').value;
  if (score > 5) {
  alert("평점은 최대 5점까지 입력 가능합니다.");
  return;
  }
  const nickname = document.getElementById('review_nickname').value.trim();

  // 유효성 검사
  if (!reviewText || !nickname) {
    alert("닉네임과 리뷰를 입력해주세요.");
    return;
  }

  // 리뷰 HTML 요소 생성
  const reviewContainer = document.getElementById('review_list');
  const tempDiv = document.createElement('div');
  tempDiv.className = 'review-item temp-review';
  tempDiv.innerHTML = `
    <p class="review-nickname"><strong>${nickname}</strong></p>
    <p class="review-text">${reviewText}</p>
    <p class="review-score">평점: ${parseFloat(score).toFixed(1)}</p>
  `;

  // 리뷰를 맨 위에 추가
  reviewContainer.prepend(tempDiv);

  // 입력칸 초기화
  document.getElementById('review_text').value = '';
  document.getElementById('review_score').value = '5';
  document.getElementById('review_nickname').value = '';
}
