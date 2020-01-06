let app = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
    deep: true,
    data: function () {
       return {
           actionText: "",
           viewWidth: 100,
           viewHeight: 100,
           camera: undefined,
           host: undefined,
           scene: undefined,
           raycaster: undefined,
           renderer: undefined,
           mousePosition: undefined,
           controls: undefined,
           // 3DView - просмотр сцены
           // select -  окно выбора
           // i2c - internal 2 cartesian dialog
           mode: "3dViews",
           i2cResult: undefined,
           mainGroup: undefined,
           labels: [],
       }
    },
    watch: {
        'mode': function (newValue) {
            this.controls.enabled = (newValue === "3dView");
        },
    },
    mounted() {
        this.mode = "i2c";
        this.initGL('app', window.innerWidth, window.innerHeight);
        this.paintGL();
    },
    computed: {
        i2cResultText() {
            if (this.i2cResult == undefined) {
                return "";
            } else {
                let ans = "x&#9;y&#9;z<br>";
                JSON.parse(this.i2cResult['cartesian']).forEach((item)=>{
                    ans += item.x + "&#9;" + item.y + "&#9;" + item.z + "<br>";
                });
                return ans;
            }
        }
    },
    methods: {
        showError(text){
            app.actionText = text;
            window.setTimeout(()=>{app.actionText = ""}, 1000);
        },
        initGL(hostid, width, height) {
            console.log('init to #' + hostid + ", width: "+width+ ", height: "+height);
            this.viewWidth = width;
            this.viewHeight = height;

            let aspect = width / height,
                host = document.getElementById(hostid);

            //camera = new THREE.OrthographicCamera(-10, 10, -10, 10, 0.1, 100)
            this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
            this.camera.position.y = 7;
            this.camera.position.z = 7;
            this.camera.lookAt(0, 0, 0);

            this.controls = new THREE.OrbitControls(this.camera);
            this.raycaster = new THREE.Raycaster();
            this.mousePosition = new THREE.Vector2();

            this.renderer = new THREE.WebGLRenderer({alpha: true});
            this.renderer.setClearColor(0xff0000, 0);
            this.renderer.setSize(width, height);

            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(0x000000);

            let lightGroup = new THREE.Group(),
                helpGroup = new THREE.Group();
            this.mainGroup = new THREE.Group();
            this.scene.add(this.mainGroup);

            lightGroup.add(new THREE.AmbientLight(0xffffff, 0.5));
            lightGroup.add(new THREE.DirectionalLight(0xffffff, 0.3));
            this.scene.add(lightGroup);

            helpGroup.add(new THREE.AxesHelper(5));
            helpGroup.add(new THREE.GridHelper(10, 10));
            this.scene.add(helpGroup);

            /*var geometry = new THREE.SphereGeometry( 1, this.spehereDetalisation, this.spehereDetalisation),
                material = new THREE.MeshPhongMaterial({
                //wireframe: true,
                color: 0x00ff00,
                specular: 0x111111
            });*/

            host.appendChild(this.renderer.domElement);
            this.host = host;
        },
        paintGL() {
            window.requestAnimationFrame(this.paintGL);

            //this.controls.update();

            //view.handleSelection();

            this.renderer.render(this.scene, this.camera);

            for (let i=0; i < app.labels.length; i++) {
                app.labels[i].updatePosition();
            }
        },
        setMode(newMode) {
            this.mode = newMode;
        },
        i2cFileOpen() {
            this.actionText = "Загрузка файла...";
            let reader = new FileReader(),
                app = this;
            reader.onload = (reader)=> {
                console.log(reader.target.result);
                this.$refs.inputField.innerHTML = reader.target.result
                    .replace(/(\r?\n+|\r+\n?)/g, '<br>');
                app.actionText = "";
                /*$.ajax({
                    method: "POST",
                    url: "/demo/internal-to-cartesian",
                    data: {
                        'text': reader.target.result
                    },
                    success(data) {
                        console.log(data);
                    },
                    error(data) {
                        console.warn(data.responseText);
                    }
                })*/

            };
            reader.readAsText(this.$refs.i2cFile.files[0]);
        },
        i2cWork() {
            this.actionText = "Обработка данных...";
            this.i2cResult = undefined;
            let txt = this.$refs.inputField.innerHTML.replace(/<br>/g, '\n');
            $.ajax({
                method: "POST",
                url: "/demo/internal-to-cartesian",
                data: {
                    'text': txt
                },
                success(data) {
                    app.actionText = "";
                    app.i2cResult = data;
                },
                error(data) {
                    app.actionText = data.responseText;
                    window.setTimeout(()=>{app.actionText = ""}, 1000);
                }
            });
        },
        i2cGo3D() {
            this.actionText = "Отправка данных для отрисовки";
            if (this.i2cResult === undefined) {
                this.actionText = "Нет данных для отображения";
                setTimeout(()=>{ app.actionText = ""}, 1000);
            } else {
                $.ajax({
                    method: "POST",
                    url: "/demo/to-3d-view",
                    data: {
                        coordinates: app.i2cResult['cartesian'],
                        labels: app.i2cResult['labels']
                    },
                    success() {
                        app.actionText = "Получение данных от сервера..."
                        app.getDataFromServer();
                    },
                    error(data) {
                        app.showError(data.responseText);
                    }
                })
            }

        },
        getDataFromServer() {
            $.ajax({
                url: "/demo/get-3d-data",
                success(data) {
                    app.showError("ОК");
                    let myData = JSON.parse(data['jsonAtoms']);

                    while (app.mainGroup.length > 0) {
                        app.mainGroup.children.pop();
                    }

                    myData.forEach((item)=>{
                        let label = app.createLabel(),
                            radius = 0.2,
                            sphereMesh = 20,
                            geometry = new THREE.SphereGeometry(
                                radius, sphereMesh, sphereMesh),
                            newMaterial = new THREE.MeshPhongMaterial({
                                color: item.color,
                                wireframe: false
                            }),
                            newMesh = new THREE.Mesh(geometry, newMaterial);

                        newMesh.position.x = item.x;
                        newMesh.position.y = item.y;
                        newMesh.position.z = item.z;

                        label.setParent(newMesh);
                        label.setHTML(item.label);
                        app.labels.push(label);
                        app.host.appendChild(label.element);

                        app.mainGroup.add(newMesh);
                    });
                    app.setMode('3dView');
                },
                error(data) {
                    app.showError(data.responseText);
                }
            })
        },
        createLabel: function () {
            let div = document.createElement('div');
            div.className = 'html-label';
            div.innerHTML = "new label";

            let thisLabel = this;

            return {
                element: div,
                parent: false,
                position: new THREE.Vector3(0, 0, 0),
                setHTML: function (html) {
                    this.element.innerHTML = html;
                },
                setParent: function (threejsobj) {
                    this.parent = threejsobj;
                },

                updatePosition: function () {
                    if (parent) {
                        this.position.copy(this.parent.position);
                    }
                    let coords2d = this.get2DCoords(this.position, app.camera);
                    this.element.style.left = coords2d.x + 'px';
                    this.element.style.top = coords2d.y + 'px';

                    console.log(coords2d.x)
                },
                get2DCoords: function (position, camera) {
                    let vector = position.project(camera);
                    vector.x = (vector.x + 1)/2 * app.host.clientWidth;
                    vector.y = -(vector.y - 1)/2 * app.host.clientHeight;
                    return vector;
                }
            }
        }
    }
});