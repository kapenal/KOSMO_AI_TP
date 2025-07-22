document.addEventListener("DOMContentLoaded", function () {
    const predictBtn = document.getElementById("predictBtn");
    const reviewInput = document.getElementById("reviewInput");

    predictBtn.addEventListener("click", async function () {
        const userReview = reviewInput.value.trim();

        if (!userReview) {
            alert("리뷰를 입력해주세요.");
            return;
        }

        try {
            const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ review: userReview })
            });

            if (!response.ok) { //200이 아니면
            throw new Error("서버 오류 또는 잘못된 요청");
            }

            //서버가 보낸 JSON 응답 파싱
            const result = await response.json();
            const label = result.label;
            const pos = result.positive;
            const neg = result.negative;

            // 감정 분석 메시지 결정
            let message = ''

            if (label.includes("Negative")) {
                message += "만족스럽지 않은 콘텐츠였나봐요.😢\n더 좋은 콘텐츠를 추천해드릴게요!";
            } 
            else {
                message += "마음에 꼭 드셨군요!😍\n더 좋은 콘텐츠를 추천해드릴게요!";
            }
            alert(message);
            console.log("긍정 확률:", pos);
            console.log("부정 확률:", neg);
        } catch (error) {
            console.error("감정 분석 실패:", error);
            alert("감정 분석 중 오류가 발생했습니다.");
        }
    });
});
