function fetchActivities(endpoint, containerSelector) {
    const title = document.createElement('h3');
    title.textContent = '최근 활동';
    const container = document.querySelector(containerSelector);
    container.appendChild(title);

    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const table = document.createElement('table');
            const thead = document.createElement('thead');
            const tbody = document.createElement('tbody');

            // 테이블 헤더 생성
            thead.innerHTML = `
                <tr>
                    <th>날짜</th>
                    <th>시간</th>
                    <th>활동</th>
                    <th>비고</th>
                </tr>
            `;

            // 테이블 바디 생성
            if (data.length > 0) {
                data.forEach(activity => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${activity.date}</td>
                        <td>${activity.time}</td>
                        <td>${activity.activity}</td>
                        <td>${activity.remark}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td colspan="4">데이터 없음</td>`;
                tbody.appendChild(tr);
            }

            // 테이블에 헤더와 바디 추가
            table.appendChild(thead);
            table.appendChild(tbody);

            // 컨테이너에 테이블 추가
            document.querySelector(containerSelector).appendChild(table);
        });
}
