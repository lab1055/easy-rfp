function readTextFile(file, id) {
        fetch("https://gist.githubusercontent.com/svdesai/c412adf96e18ba097b09fd5239f59585/raw/81ed850068240b57e4b0918fcb7e49fe1471d1ae/logs.txt")
        .then((response) => {
            response.json().then(({text_out}) => {
            	console.log(text_out)
                document.getElementById(id).innerHTML = text_out;
            })
        });
    }

readTextFile("randomText.txt", "text-wala-comp")