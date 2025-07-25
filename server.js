// server.js
const express = require('express');
const app = express();
const port = 3000;
const { spawn } = require('child_process');
const path = require("path");
const { urlencoded } = require('body-parser');
const { exec } = require("child_process"); // 맨 위에 이미 있지 않다면 추가
const axios = require('axios'); // FastAPI와 통신하기 위한 axios 추가
// 추가한 바디 파싱
app.use(express.urlencoded({ extended: true }));
// JSON 파싱 미들웨어 추가
app.use(express.json());

// 정적 파일 제공 (HTML, JS 파일을 제공)
app.use(express.static('public')); // index.html과 script.js를 제공

// 기본 라우트 처리 - index.html로 연결
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'html', 'index.html'));
});

// POST 요청 처리 -> GET 요청 처리로 변경
app.get('/now_screen', (req, res) => {
    console.log('현재 상영작 요청(GET) 들어옴');

    const pythonProcess = spawn(
        'python',
        [path.join(__dirname, "public",  "py", "search_movies.py")] // 인자 없이 호출
    );

    let dataBuffer = "";

    pythonProcess.stdout.on('data', (data) => {
        dataBuffer += data.toString();
    });

    pythonProcess.stdout.on('end', () => {
        try {
            const output = JSON.parse(dataBuffer);
            res.json({ movies: output });  // movies 키로 결과 JSON 반환
        } catch (error) {
            console.error('JSON 파싱 오류:', error);
            res.status(500).json({ error: 'Python 결과 처리 중 오류 발생' });
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data.toString()}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
});


// POST 요청 처리
app.post('/search_movie', (req, res) => {
    const searchText = req.body.text;  // 클라이언트에서 보낸 'text' 값
    console.log(searchText + ' 버튼이 클릭되었어요!');

    // Python 스크립트 실행
    const pythonProcess = spawn(
        'python',
        // [path.join(__dirname, "public",  "py", "search_movies.py"), searchText]
        [path.join(__dirname, "public",  "py", "search_movies_list.py"), searchText]
    );
    
    // Python 프로세스 실행 후 결과 처리
    pythonProcess.stdout.on('data', (data) => {
        try {
            const output = JSON.parse(data.toString()); // 반환된 main.py의 search_url이 data 매개변수로 받아옴
            // console.log("movie_title", output)
            // searchURL을 클라이언트(script.js) 반환
            res.json({ movies : output });
        } catch (error) {
            console.error('JSON 파싱 오류:', error);
            res.status(500).json({ error: 'Python 결과 처리 중 오류 발생' });
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data.toString()}`);
        res.status(500).json({ error: 'Python 스크립트 실행 중 오류 발생' });
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
});


// POST 요청 처리 - 영화 추천
app.get('/api/recommend', (req, res) => {
    const title = req.query.title;
    console.log(`${title} 추천 요청이 들어왔어요!`);

    const pythonProcess = spawn(
    "C:\\ProgramData\\anaconda3\\python.exe",  // ← Python 경로
    [path.join(__dirname, "public", "py", "recommend.py"), title]
    );

    let dataBuffer = '';
    let errorBuffer = '';

    pythonProcess.stdout.on('data', (chunk) => {
    dataBuffer += chunk.toString('utf8');
    });

    pythonProcess.stderr.on('data', (chunk) => {
    errorBuffer += chunk.toString('utf8');
    });

    pythonProcess.on('close', (code) => {
    if (code !== 0) {
        console.error(`Python 추천 프로세스 종료 코드: ${code}`);
        console.error(`stderr: ${errorBuffer}`);
        return res.status(500).json({ error: '추천 스크립트 실행 실패' });
    }

    try {
        const output = JSON.parse(dataBuffer);
        console.log("추천 결과:", output);
        res.json({
        input_title: output.input_title,
        recommendations: output.recommendations
        });
    } catch (error) {
        console.error('추천 JSON 파싱 오류:', error);
        console.error('원본:', dataBuffer);
        res.status(500).json({ error: '추천 결과 처리 중 오류 발생' });
    }
    });
});

// 상세 페이지 HTML 제공
app.get('/movie/:id', (req, res, next) => {
    res.sendFile(path.join(__dirname, 'public', 'html', 'detail_page.html'));
});

// 영화 상세 데이터 API
app.get('/api/movie/:id', (req, res, next) => {
    const movieId = req.params.id;
    const id = req.params.id;
    if (id.endsWith('.html')) {
    // 아마 정적 파일 요청일 가능성이 있으니 다음 미들웨어로 넘김
    return next();
}
    console.log(`API 요청 받은 movieId: ${movieId}`);

    const python = spawn('python', [path.join(__dirname, 'public', 'py', 'movie_detail.py'), movieId]);

        let data = '';
        let error = '';

        python.stdout.on('data', chunk => {
        data += chunk.toString();
    });

    python.stderr.on('data', chunk => {
        error += chunk.toString();
    });

    python.on('close', code => {
        if (code !== 0) {
        console.error(`Python 프로세스 종료 코드: ${code}`);
        console.error('stderr:', error);
        return res.status(500).json({ error: 'Python 실행 실패' });
    }

    if (error) {
        console.error('Python STDERR:', error);
    }

    try {
        const movie = JSON.parse(data);
        // console.log("영화 상세 데이터:", movie);
        res.json(movie);
    } catch (e) {
        console.error('JSON 파싱 실패:', e);
        console.error('원본 데이터:', data);
        res.status(500).json({ error: '응답 처리 실패' });
    }
    });
});

app.get('/api/review/:id', (req, res) => {
    const movieId = req.params.id;
    console.log(`리뷰 요청 받은 movieId: ${movieId}`);

    const python = spawn('python', [path.join(__dirname, 'public', 'py', 'movie_detail_review.py'), movieId]);

    let data = '';
    let error = '';

    python.stdout.on('data', chunk => {
        data += chunk.toString();
    });

    python.stderr.on('data', chunk => {
        error += chunk.toString();
    });

    python.on('close', code => {
        if (code !== 0) {
            console.error(`Python 프로세스 종료 코드: ${code}`);
            console.error('stderr:', error);
            return res.status(500).json({ error: 'Python 실행 실패' });
        }

        if (error) {
            console.error('Python STDERR:', error);
        }

        try {
            const reviews = JSON.parse(data);
            console.log("영화 리뷰 데이터:", reviews);
            res.json(reviews);
        } catch (e) {
            console.error('JSON 파싱 실패:', e);
            console.error('원본 데이터:', data);
            res.status(500).json({ error: '응답 처리 실패' });
        }
    });
});

app.get('/api/wordbubble/:id', (req, res) => {
    const movieId = req.params.id;
    console.log(`리뷰 단어 빈도 요청 받은 movieId: ${movieId}`);

    const python = spawn('python', [path.join(__dirname, 'public', 'py', 'chart.py'), movieId]);

    let data = '';
    let error = '';

    python.stdout.on('data', chunk => {
        const chunkStr = chunk.toString();
        console.log("Python stdout:", chunkStr); // 전체 출력 로그 확인
        data += chunkStr;
    });

    python.stderr.on('data', chunk => {
        const errStr = chunk.toString();
        console.error("Python stderr:", errStr);
        error += errStr;
    });

    python.on('close', code => {
        if (code !== 0) {
        console.error(`Python 프로세스 종료 코드: ${code}`);
        return res.status(500).json({ error: 'Python 실행 실패', details: error });
    }

        try {
            // JSON 배열만 추출
            const jsonMatch = data.match(/\[[\s\S]*?\]/);  // 첫 번째 대괄호 배열 추출 (개행 포함 허용)
            if (!jsonMatch) {
                throw new Error('JSON 배열을 찾을 수 없음');
            }

            const words = JSON.parse(jsonMatch[0]);

            if (!Array.isArray(words) || words.length === 0) {
                console.error('데이터가 배열이 아니거나 비어있습니다:', words);
                return res.status(500).json({ error: '올바른 배열 형식이 아닙니다.' });
            }

            console.log("Parsed words:", words);
            res.json(words);
            } catch (e) {
            console.error('JSON 파싱 실패:', e);
            console.error('원본 데이터:', data);
            res.status(500).json({ error: '응답 처리 실패', details: e.message });
        }
    });
});


// 미주꺼--------------------------------------------------
app.use(express.static(path.join(__dirname, 'public')));

// 리뷰 감정 분석 요청
app.post('/api/predict', (req, res) => {
    const userReview = req.body.review;
    console.log("감정 분석 요청:", userReview);

    const pythonScriptPath = path.join(__dirname, 'public', 'py', 'RecommendMovie.py');

    exec(`python "${pythonScriptPath}" "${userReview}"`, (error, stdout, stderr) => {
        if (error) {
            console.error("감정 분석 실행 오류:", error);
            return res.status(500).json({ error: '감정 분석 실패' });
        }
        
        try {
            const result = JSON.parse(stdout);
            res.json(result);
        } catch (parseError) {
            console.error("감정 분석 결과 파싱 오류:", parseError);
            console.error("stdout:", stdout);
            res.status(500).json({ error: '결과 파싱 실패' });
        }
    });
});

//-------------------------------------------------------

// 챗봇
// 클라이언트가 질문 보내면 FastAPI에 전달 후 결과 응답
app.post('/ask', async (req, res) => {
    const {question } = req.body;
    console.log('[REQ DEBUG] question:', question);  // 🔍 여기서 실제 질문을 확인하세요
    try {
        const response = await axios.post('http://localhost:8000/qa', {
        question
        });
        res.json({ answer: response.data.answer });
    } catch (error) {
        console.error('FastAPI 호출 에러:', error.message);
        res.status(500).json({ answer: '서버 에러가 발생했습니다.' });
    }
});


// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
});


