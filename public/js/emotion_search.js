document.addEventListener("DOMContentLoaded", () => {
    const submitBtn = document.getElementById("submit_review");
    const reviewInput = document.getElementById("review_text");
    const authorInput = document.getElementById("review_author");

    submitBtn.addEventListener("click", async () => {
        const userReview = reviewInput.value.trim();
        const author = authorInput.value.trim() || "익명";

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

            if (!response.ok) {
                throw new Error("서버 오류 또는 잘못된 요청");
            }

            const result = await response.json();
            const label = result.label;
            const pos = result.positive;
            const neg = result.negative;

            let message = '';

            if (label === "Negative") {
                message += `'${author}'님, 만족스럽지 않은 콘텐츠였나봐요.😢\n더 좋은 콘텐츠를 추천해드릴게요!`;
            } else {
                message += `'${author}'님, 마음에 꼭 드셨군요!😍\n더 좋은 콘텐츠를 추천해드릴게요!`;
            }

            alert(message);
        } catch (error) {
            console.error("감정 분석 실패:", error);
            alert("감정 분석 중 오류가 발생했습니다.");
        }
    });
});
