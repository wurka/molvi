"use strict";
//import getCookie from "mycookie";
//import * as THREE from "./three";

class Settings {
    constructor() {
        this.openFileUrl = "/molvi/server/open-file-dialog";
        this.loadActiveFileUrl = "/molvi/get-last-mol-file";
        this.loadMolFileUrl = "/molvi/get-mol-file";
        this.loadDocumentUrl = "/molvi/get-document";
        this.saveDocumentToServerUrl = "/molvi/save-document";
        this.sphereDetalisation = 20;  // количество полигонов при отрисовке сферических объектов
        this.getDocumentsUrl = "/molvi/get-documents"; // запрос документов на сервере
        this.getMolsUrl = "/molvi/get-mol-files"; // запрос .mol файлов на сервере
    }
}
var settings = new Settings();
var lastId = 0;
/**
 * Сгенерировать id
 */
function getId() {
    lastId += 1;
    return lastId;
}


/**
 * Класс для хранения информации об атомах
 */
class Atom {
    constructor(x, y, z, name) {
        this.x = x;  //координата х (ангстрем)
        this.y = y;  //координата y (ангстрем)
        this.z = z;  //координата z (ангстрем)
        this.name = name;
        this.color = "#ff0000";  //цвет атома
        //this.selected = false;  //выбран ли атом
        this.mass = 0;
        this.id = getId();
    }
}

/**
 * Набор атомов (кластер)
 */
class Cluster {
    constructor() {
        this.atomList = [];
        this.caption = "noname custler";
        this.id = getId();
    }
}

/**
 * Информация о связи
 */
class Link {
    constructor(fromId, toId) {
        this.id = getId();
        this.from = fromId;
        this.to = toId;
    }
}

/**
 * Документ, хранящий информацию о рабочей области
 */
class MolviDocument {
    constructor() {
        this.links = [];
        this.clusters = [];
        this.documentName = "no name"
    }
}

/**
 * Функции "ядра". Взаимодействие с сервером и т.п.
 */
class MolviEngine {
    constructor() {
        this.linkCreationSource = []; //массив id для создания связи
        //this.controlMode = "none";  //режим управления
    }

    documentList2Explorer() {
        $.ajax({
            url: settings.getDocumentsUrl,
            error: function (data) {
                console.error(data);
            },
            success: function (data) {
                var html = "",
                    htmlChunk = "<div class=\"file\" id='[+id]' onclick='$(\"#openFIleDialog>.fileView>.file\").removeClass(\"selected\"); $(this).toggleClass(\"selected\")' ondblclick='$(\"#openFileDialog .mybutton:first-child\").click()'>[+content]</div>",
                    dict = JSON.parse(data);

                dict.forEach(function (item) {
                    html += htmlChunk.replace('[+content]', item).replace('[+id]', "file_" + item);
                });
                $("#openFileDialog>.fileView").html(html);
            }
        });
    }

    molList2Explorer() {
        $.ajax({
            url: settings.getMolsUrl,
            error: function (data) {
                $("#openFileDialogMol>.fileView").html(data.responseText);
            },
            success: function (data) {
                var html = "",
                    htmlChunk = "<div class=\"file\" id='[+id]' onclick='$(\".openFIleDialog>.fileView>.file\").removeClass(\"selected\"); $(this).toggleClass(\"selected\")'  ondblclick='$(\"#openFileDialogMol .mybutton:first-child\").click()' >[+content]</div>",
                    dict = JSON.parse(data);

                dict.forEach(function (item) {
                    html += htmlChunk.replace('[+content]', item).replace('[+id]', "file_" + item);
                });
                $("#openFileDialogMol>.fileView").html(html);
            }
        });
    }

    /**
     * Загрузка выбранного в списке fileView файла     *
     */
    openFileDialog_loadSelected() {
        var element = $("#openFileDialog .selected"),
            fileName = "";

        view.enableControls();

        if (element.length === 0) {
            alert("Выберите файл для загрузки ИЛИ нажмите Отмена");
        } else {
            fileName = element.html();
            console.log(fileName);

            $.ajax({
                url: settings.loadDocumentUrl,
                data: {
                    'document-name': fileName
                },
                error(data) {
                    $("#openFileDialog .fileView").html(data.responseText);
                },
                success(data) {
                    $("#openFileDialog .fileView").html("обработка ответа");
                    try {
                        var doc = JSON.parse(data);
                        console.log(doc);
                    } catch (err) {
                        $("#openFileDialog .fileView").html("Error: " + err.message);
                    }
                }

            });
            //view.closeOpenFileDialog();
        }
    }

    /**
     * Загрузка выбранного в списке fileView (.mol) файла     *
     */
    openFileDialogMol_loadSelected(deleteold=true) {
        var element = $("#openFileDialogMol .selected"),
            fileName = "";

        view.enableControls();

        if (element.length === 0) {
            alert("Выберите файл для загрузки ИЛИ нажмите Отмена");
        } else {
            fileName = element.html();
            console.log(fileName);

            $.ajax({
                url: settings.loadMolFileUrl,
                data: {
                    'filename': fileName
                },
                error(data) {
                    $("#openFileDialogMol .fileView").html(data.responseText);
                },
                success(data) {
                    // получен json файл с информацией о молекуле
                    console.log(data);
                    try {
                        engine.buildAtomData(data, deleteold);
                        view.closeOpenFileDialog();
                    } catch (err) {
                        $("#openFileDialogMol .fileView").html("ERROR: " + err.message);
                    }

                }
            });

        }
    }

    /**
     * Построить Html объекты из "документа"
     */
    buildHtmlFromDoc() {        
        var ahtml = "",
            mhtml,
            buf,
            html = "";        
        doc.clusters.forEach(function(cluster) {
            ahtml = "";
            cluster.atomList.forEach(function (atom) {
                buf = Chunks.atom.replace(/\[\[id]]/g, atom.id);
                buf = buf.replace(/\[\[name]]/g, atom.name);
                buf = buf.replace(/\[\[x]]/g, atom.x);
                buf = buf.replace(/\[\[y]]/g, atom.y);
                buf = buf.replace(/\[\[z]]/g, atom.z);
                ahtml += buf;
            });

            mhtml = Chunks.cluster.replace(/\[\[data]]/g, ahtml);
            mhtml = mhtml.replace(/\[\[title]]/g, cluster.caption);
            mhtml = mhtml.replace(/\[\[id]]/g, cluster.id);
            html += mhtml;
        });
        
        var linkshtml = "",
            newHtml = "",
            chunk = Chunks.link;
        doc.links.forEach(function (link) {
            newHtml = chunk.replace(/\[FROM]/g, link.from);
            newHtml = newHtml.replace(/\[TO]/g, link.to);
            newHtml = newHtml.replace(/\[ID]/g, link.id);
            linkshtml += newHtml;
        });

        $(".atomsView").html(html);
        $(".linksView").html(linkshtml);
    }

    selectionMaterial(){
        var ans = new THREE.MeshPhongMaterial({
            color: 0xef2500
        });
        return ans;
    }

    /**
     * Материал для атома с именем atomName (H, C, Zn и т.п.)
     */
    buildAtomMaterial(atomName){
        var ans = new THREE.MeshPhongMaterial({
            color: MolviConf.getAtomColor(atomName),
            wireframe: false
        });
        return ans;
    }

    /**
     * Потроить 3D представление THREE.Mesh[] и THREE.Group[]
     * по информации, хранящейся в "документе"
     */
    build3DFromDoc() {
        //освобождение памяти
        while (view.atomGroup.children.length > 0) {
            view.atomGroup.children[0] = null;
            view.atomGroup.children.splice(0, 1);
        }

        doc.clusters.forEach(function (cluster) {
            cluster.atomList.forEach(function (atom) {
                var x = parseFloat(atom.x),
                    y = parseFloat(atom.y),
                    z = parseFloat(atom.z),
                    radius = MolviConf.getAtomRadius(atom.name),
                    sd = settings.sphereDetalisation,
                    geometry = new THREE.SphereGeometry(radius, sd, sd),
                    material = engine.buildAtomMaterial(atom.name),
                    mesh = new THREE.Mesh(geometry, material);

                mesh.position.x = x;
                mesh.position.y = y;
                mesh.position.z = z;
                view.atomGroup.children.push(mesh);
            });
        });

        //удаление старых Mesh'эй
        while (view.linkGroup.children.length > 0) {
            view.linkGroup.children[0] = null;
            view.linkGroup.children.splice(0, 1);
        }
        //создание Mesh'ей
        doc.links.forEach(function (link) {
            var atom1 = null,
                atom2 = null;

            doc.clusters.forEach(function (cluster) {
                cluster.atomList.forEach(function (atom) {
                    if (atom.id == link.from) {
                        atom1 = atom;
                    }
                    if (atom.id == link.to) {
                        atom2 = atom;
                    }
                });
            });

            if (atom1 == null) {
                console.error("atom 1 not finded!");
                return;
            }
            if (atom2 == null) {
                console.error("atom 2 not finded!");
                return;
            }

            var lineMesh = view.buildLineMesh(atom1.x, atom1.y, atom1.z, atom2.x, atom2.y, atom2.z, 0xf6ff0f);
            view.linkGroup.add(lineMesh);

        })
    }

    /**
     * Показать сообщение для пользователя 
     * (вызов без аргументов спрячет поле сообщений)
     */
    static userMessage(message) {
        "use strict";
        if (!message){
            $("#infoMessageField").hide();
        } else {
            $("#infoMessageText").html(message);
            $("#infoMessageField").show();
        }
    }

    static onMouseMove(event) {
        view.mousePosition.x = (event.offsetX / view.viewWidth) * 2 - 1;
        view.mousePosition.y = - (event.offsetY / view.viewHeight) * 2 + 1;
    }

    static onMouseDown(/*event*/) {

        //ids = []
        /*var id = -1,
            distance = -1,
            atoms = atomGroup.children;

        for (var i = 0; i < highlighted.length; i++) {
            for (var j = 0; j < atoms.length; j++) {
                if (atoms[j] == highlighted[i].object){
                    //ids.push(j);
                    if (
                        (distance < 0) ||
                        (highlighted[i].distance <= distance)){
                        id = j;
                        distance = highlighted[i].distance;
                    }
                }
            }
        }*/

        /*if (highlighted.length > 0) {
         selectedAtoms = [];
         for (var i = 0; i < highlighted.length; i++){
         selectedAtoms.push(highlighted[i].object);
         }
         }

         selectedIds = []
         for (var i = 0; i < atoms.length; i++){
         for (var j = 0; j < selectedAtoms.length; j++){
         if (selectedAtoms[j] == atoms[i]){
         selectedIds.push(i);
         }
         }
         }
         console.log(selectedIds);*/
        /*if (id >= 0) {
            selectFromIds([id]);
        }*/
    }

    /**
     * Создание связи
     * @param {Array} ids массив id для создания связи [] или [id]
     */
    linkCreation(ids){
        "use strict";
    
        console.log(ids);
        // не выбрано ниодного атома
        if (!ids) {
            this.linkCreationSource = [];
            
            userMessage("Выберите атом #1");
            return;
        }
    
        //ids содержит что-то
        if (ids.length != 1) {
            console.warn("Only array with length == 1 allowed");
            return;
        }
        if (this.linkCreationSource.length == 0){
            this.linkCreationSource.push(ids[0]);
            MolviEngine.userMessage("Выберите атом #2");
        } else if (this.linkCreationSource.length == 1){
            this.linkCreationSource.push(ids[0]);
            MolviEngine.userMessage();
            var newLink = new WLink(this.linkCreationSource[0], this.linkCreationSource[1]),
                p1 = atomGroup.children[newLink.from].position,
                p2 = atomGroup.children[newLink.to].position,
                linkLine = buildLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, linkMaterial);
            addLink(newLink);
            console.log(newLink);
            console.log(atomGroup);
            selectMode('none');
        }

        
    }

    /**
     * Обработчик нажатия клавиши, когда в фокусе кнопка "автотрассировка"
    */
    autoTraceKeyPressed(e) {
        view.controls.enabled = false;
        if (e.keyCode == 13){   //нажата кнопка Enter
            engine.executeAutoTrace();
        }
    }

    /**
     * Режим работы с пользователем
     * @param {String} modeName Название режима
     */
    selectMode(modeName){
        "use strict";
        $(".selectedIcon").hide();
        $(".unselectedIcon").show();
        this.controlMode = modeName;
    
        if(modeName === 'line'){
            $("#icon_modeLineUnselected").hide();
            $("#icon_modeLineSelected").show();
            this.linkCreation([]);
        }
    }

    LoadAtomDataFromServer(deleteold) {
        var url = settings.loadActiveFileUrl;

        $.ajax({
            url: url,
            success: function(data){
                // $(".atomsView").html(data); !!!!!
                console.log("LoadAtoms: data loading OK")
                engine.buildAtomData(data, deleteold);
                console.log(data);
            },
            error: function(data) {
                $(".atomsView").html(data.responseText);
                console.log("ERROR")
                console.log(data)
            }
        })
    }

    LoadMolFromServer(deleteold) {

    }



    /**
     * Создание объектов для содержания информации об атомах
     * @param jsonString информация об атомах
     * @param deleteOld true => удалить все старые атомы
     */
    buildAtomData(jsonString, deleteOld){
         //создание рабочего документа (хранит всю рабочую инфу)

        if (deleteOld) {
            doc = new MolviDocument();
        }
        var newCluster = new Cluster();
        newCluster.caption = "Кластер " + (doc.clusters.length + 1).toString();
        doc.clusters.push(newCluster);

        var atar = JSON.parse(jsonString);

        atar.forEach(function(item, indx){
            var x = parseFloat(item['x']),
                y = parseFloat(item['y']),
                z = parseFloat(item['z']),
                mass = parseFloat(item['mass']),
                name = item['name'],
                newAtom = new Atom(x, y, z, name);
                newAtom.mass = mass;

            newCluster.atomList.push(newAtom);
        });
        engine.buildHtmlFromDoc();
        engine.build3DFromDoc();

        //reset to default view
        view.resetCamera();
    }

    openPlusFileDialog() {
        $.ajax({
            url: settings.openFileUrl,
            success: function(data) {
                console.log(data);
                var ans = data.slice(-6);
                if (ans === "<br>OK"){
                    //имя активного файла не сервере успешно изменено
                    console.log("OK");
                    //buildScene();
                    //paintGL();
                    engine.LoadAtomDataFromServer(false);
                } else {
                    console.warn(data);
                }
            },
            error: function(data) {
                alert("Ошибка при открытии файла")
                console.log("open file error: " + data.toString())
            }
        })
    }

    /**
     * Открыть элементы управления для переноса кластера
     * @param clusterId id кластера, который требуется перенести
     */
    openMoveControls(clusterId){
        "use strict"

        $("#moveMoleculaId").html(clusterId)
        $('#moleculaMoveControls').show()

        $("#moveControl_x").val(0)
        $("#moveControl_y").val(0)
        $("#moveControl_z").val(0)

        view.controls.enabled = false
    }

    /**
     * Закрыть элементы управления для переноса кластера
     */
    closeMoveControls(){
        view.controls.enabled = true
        $('#moleculaMoveControls').hide()
    }

    doMoleculaMove() {
        var xshift = $("#moveControl_x").val(),
            yshift = $("#moveControl_y").val(),
            zshift = $("#moveControl_z").val(),
            id = $("#moveMoleculaId").html();
        xshift = parseFloat(xshift);
        yshift = parseFloat(yshift);
        zshift = parseFloat(zshift);
        id = parseInt(id, 10);
        if (isNaN(xshift) || isNaN(yshift) || isNaN(zshift)){
            console.log("Parse error!");
            $("#moleculaMoveControls").hide();
            return;
        }
        console.log('doMoleculaMove, id: ');
        console.log(id);
        var cluster = null;
        doc.clusters.forEach(function (clust) {
            if (clust.id == id) {
                cluster = clust;
                return;
            }
        });
        if (cluster === null) {
            console.error("No cluster found. with id: " + id.toString());
        } else {
            cluster.atomList.forEach(function (atom) {
                atom.x += xshift;
                atom.y += yshift;
                atom.z += zshift;
            });
        }
        engine.closeMoveControls();

        engine.buildHtmlFromDoc();
        engine.build3DFromDoc();
    }

    executeAutoTrace() {
        var radius = 1.6,
            re = document.getElementById('traceRange').value;
        radius = parseFloat(re, 10);
        if (isNaN(radius)) {
            console.log("Error in parse int");
            alert('Введите корректное значение длины автотрассировки');
            return;
        }

        //удаление старых связей
        while(doc.links.length > 0) {
            doc.links[0] = null;
            doc.links.splice(0, 1);
        }

        var rmin,
            numberj;

        doc.clusters.forEach(function (cluster1) {
           doc.clusters.forEach(function (cluster2) {
               cluster1.atomList.forEach(function (atom1) {
                   cluster2.atomList.forEach(function (atom2) {
                       if (atom1.id == atom2.id) {
                           return;
                       } else {
                           var r1 = Math.pow(atom1.x - atom2.x, 2),
                               r2 = Math.pow(atom1.y - atom2.y, 2),
                               r3 = Math.pow(atom1.z - atom2.z, 2),
                               r = Math.sqrt(r1 + r2 + r3);

                           if(r <= radius) {
                               var newlink = new Link(atom1.id, atom2.id);
                               doc.links.push(newlink);
                           }
                       }
                   })
               });
           }) ;
        });

        //ревизия созданных связей
        doc.links.forEach(function(link1) {
            doc.links.forEach(function(link2, ind) {
                if ((link1.from == link2.from) && (link1.to == link2.to)) //это одна и та же связь
                    return;

                if ((link2.to == link1.from) && (link2.from == link1.to)) { // связи разные, но одинаковые
                    doc.links.splice(ind, 1);
                }
            });
        });

        engine.buildHtmlFromDoc();
        engine.build3DFromDoc();
    }

    saveDocumentToServer() {
        var mydoc = {
            "documentName": $("#saveFileName").val(),
            "clusters": [],
            "links": []
        };

        // заполнение поля clusters
        doc.clusters.forEach(function (cluster) {
            var myCluster = {
                "caption": cluster.caption,
                "id": cluster.id,
                "atoms": []
            }
            //заполнение атомов кластера
            cluster.atomList.forEach(function (atom) {
                var myatom = {
                    x: atom.x,
                    y: atom.y,
                    z: atom.z,
                    name: atom.name,
                    mass: atom.mass
                }
                myCluster.atoms.push(myatom);
            });
            mydoc.clusters.push(myCluster);
        });

        //заполнение поля links
        doc.links.forEach(function (link) {
            var af = null,
                at = null;

            doc.clusters.forEach(function (cluster) {
                cluster.atomList.forEach(function (atom) {
                    if (atom.id == link.from) {
                        af = atom;
                    }
                    if (atom.id == link.to) {
                        at = atom;
                    }
                });
            });

            if ((af == null) || (at == null)) {
                console.error("af or at is null");
            } else {
                var mylink = {
                    "fromx": af.x,
                    "fromy": af.y,
                    "fromz": af.z,
                    "tox": at.x,
                    "toy": at.y,
                    "toz": at.z
                };
                mydoc.links.push(mylink);
            }
        });

        var json = JSON.stringify(mydoc),
            csrf_token = $("input[name=csrfmiddlewaretoken]").val();
        $.ajax({
            method: "POST",
            url: settings.saveDocumentToServerUrl,
            data: {
                document: json,
                csrfmiddlewaretoken: csrf_token
            },
            success: function(data){
                if (data == "OK"){
                    console.log("document saved");
                    $("#errorMessage").html("");
                } else {
                    $("#errorMessage").html(data);
                }
            },
            error: function(data, x){
                MolviEngine.userMessage("Ошибка при сохранении документа на сервер");
                console.error(data);
                $("body").html(data.responseText);
            }
        });
    }
}

/**
 * Класс для работы с 3D отображением (требуется three.js)
 */
class MolviView {
    constructor() {
        "use strict";
        this.scene = new THREE.Scene();
        this.lightGroup = new THREE.Group();
        this.lightGroup.name = "lightGroup";
        this.helpGroup = new THREE.Group();
        this.helpGroup.name = "helpGroup";
        this.linkGroup = new THREE.Group();
        this.linkGroup.name = "linkGroup";
        this.atomGroup = new THREE.Group();
        this.atomGroup.name = "atomGroup";
        this.outlinesGroup = new THREE.Group();
        this.outlinesGroup.name = "outlines group";
        this.engine = null;
        this.renderer = new THREE.WebGLRenderer({alpha: true});
        this.camera = null;
        this.controls = null;
        this.viewHeight = 50;
        this.viewWidth = 50;
    }

    init() {
        "use strict"
        this.initGL("display", 600, 600);
        this.buildScene();
        MolviView.paintGL();
    }

    addLight() {
        console.log('addLight');
    }

    initGL(hostid, width, height) {
        view.viewWidth = width;
        view.viewHeight = height;

        var aspect = width / height,
            host = document.getElementById(hostid);

        //camera = new THREE.OrthographicCamera(-10, 10, -10, 10, 0.1, 100)
        view.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        view.camera.position.z = 3;
    
        view.controls = new THREE.OrbitControls(this.camera);
        view.raycaster = new THREE.Raycaster();
        view.mousePosition = new THREE.Vector2();
    

        view.renderer.setClearColor(0xff0000, 0);
        view.renderer.setSize(width, height);

        view.scene.background = new THREE.Color(0x000000);
        view.addLight();
    
        /*var geometry = new THREE.SphereGeometry( 1, this.spehereDetalisation, this.spehereDetalisation),
            material = new THREE.MeshPhongMaterial({
            //wireframe: true,
            color: 0x00ff00,
            specular: 0x111111
        });*/

        host.appendChild(this.renderer.domElement);
    }

    static paintGL() {
        requestAnimationFrame(MolviView.paintGL);

        //this.controls.update();

        view.handleSelection();

        view.renderer.render(view.scene, view.camera);
    }

    buildScene() {
        view.scene.background = new THREE.Color(0x000000);
        view.scene.children.splice(0, this.scene.children.length);
        
        //добавить свет
        var light1 = new THREE.DirectionalLight(0xffffff, 0.3),
            light2 = new THREE.AmbientLight(0xffffff, 0.5);

        view.lightGroup.add(light1);
        view.lightGroup.add(light2);
        view.scene.add(this.lightGroup);
    
        //добавить вспомогательные элементы
        var helper = new THREE.AxesHelper(22),
            grid = new THREE.GridHelper(10, 10);
        view.helpGroup.add(grid);
        view.helpGroup.add(helper);
        view.scene.add(view.helpGroup);
    
        //добавить хранилище под молекулы
        view.scene.add(view.atomGroup);
    
        //добавить связи между молекулами
        view.scene.add(this.linkGroup);
    
        //добавить объекты для выделения
        view.scene.add(this.outlinesGroup);
    }

    buildLineMesh(x1, y1, z1, x2, y2, z2, colorHex) {
        var array = new Float32Array([x1, y1, z1, x2, y2, z2]),
            color = new THREE.Color(colorHex),
            material = new MeshLineMaterial({
                color: color,
                opacity: 1,
                lineWidth: 0.03
            });

        var temp = new MeshLine();
        temp.setGeometry(array);
        var geom = temp.geometry;

        var mesh = new THREE.Mesh(geom, material);
        return mesh;
    }

    resetCamera() {
        view.camera.position.x = 0;
        view.camera.position.y = 5;
        view.camera.position.z = 0;
        view.camera.lookAt(0,0,0);
    }

    enableControls(){
        view.controls.enabled = true;
    }
    disableControls(){
        view.controls.enabled = false;
    }

    /**
     * Обработка наведения на элементы
     */
    handleSelection(){
        view.raycaster.setFromCamera(view.mousePosition, view.camera);
        //console.log(mousePosition);

        var atoms = view.atomGroup.children,
            intersects = view.raycaster.intersectObjects(atoms);


        var highlighted = [];
        for (var i = 0; i < atoms.length; i++){
            atoms[i].material =  engine.buildAtomMaterial(atoms[i].name);
        }

        for (var i = 0; i < intersects.length; i++) {
            intersects[i].object.material = engine.selectionMaterial();
            highlighted.push(intersects[i]);
        }

        // изменение материала выделенных атомов
        /*for (var i = 0; i < selectedAtoms.length; i++) {
            selectedAtoms[i].material = selectionMaterial;
        }*/
    }



    showSaveFileDialog() {
        $('#saveFileDialog').show();
        view.disableControls();
        $('#saveFileName').focus();
        $('#saveFileName').select();
    }

    openFileDialog(mode) {
        console.log(typeof(mode));
        if (mode == "document") {
            $("#openFileDialog").show();
            engine.documentList2Explorer();
            view.disableControls()
        } else if (mode == "mol") {
            $("#openFileDialogMol").show();
            engine.molList2Explorer();
            var handler = 'engine.openFileDialogMol_loadSelected(true)';
            $("#openFileDialogMol .mybutton:first-child").attr('onclick', handler);
            view.disableControls()
        } else if (mode == 'plusmol') {
            $("#openFileDialogMol").show();
            engine.molList2Explorer();
            var handler = 'engine.openFileDialogMol_loadSelected(false)';
            $("#openFileDialogMol .mybutton:first-child").attr('onclick', handler);
            view.disableControls();
        }
    }

    closeOpenFileDialog() {
        $('.openFileDialog').hide();
        view.enableControls();
    }

    moveAction(id) {
        $(".moveActionContent").hide();
        $("." + id + "_content").show();
        $(".moveAction").removeClass("selected");
        $("#" + id).addClass("selected");
    }
}

var engine = new MolviEngine(),
    view = new MolviView(),
    doc = new MolviDocument();

$(document).ready(function(){
    engine.view = view;
    view.engine = engine;
    MolviEngine.instance = engine;
    MolviView.instance = view;


    MolviEngine.userMessage();

    engine.selectMode("none");
    //добавление обработчиков
    var display = document.getElementById("display");
    display.addEventListener("mousemove",  MolviEngine.onMouseMove, false);
    display.addEventListener("mousedown",  MolviEngine.onMouseDown, false);

    view.init();
    
    //LoadAtoms(true);

    var inputElement = document.getElementById('traceRange');
    inputElement.onkeypress = engine.autoTraceKeyPressed;
    inputElement.value = 1.6;

    //загрузить активный файл с сервера
    engine.LoadAtomDataFromServer(true);
});