"use strict";
//import getCookie from "mycookie";
//import * as THREE from "./three";
function count(obj) {
    if (obj.__count__ !== undefined) { // Old FF
        return obj.__count__;
    }

    if (Object.keys) { // ES5
        return Object.keys(obj).length;
    }

    // Everything else:
    let c = 0, p;
    for (p in obj) {
        if (obj.hasOwnProperty(p)) {
            c += 1;
        }
    }
    return c;
}

let app = new Vue({
    el: '#app',
    delimiters: ["[[", "]]"],
    data: {
        controlMode: 'idle',  // активный режим (idle, 'dihedral creation')
        optimisationLoading: true,
        optimisers: [],
        atoms: {},
        links: [],
        clusters: [{}],
        valenceAngles: [],
        dihedralAngles: [],  // список двугранных углов
        documentName: "new document",
        selectedAtomIds: [],
        selectedLinkIds: []
    },
    computed: {
        noValenceAngles: function () {
            return this.length === 0;
        }
    },
    methods: {
        selectOption(optionId) {
            console.log(optionId);
            app.optimisers.forEach((opt)=>{
                if (opt.id === parseInt(optionId)) {
                    opt.selected = !opt.selected;
                }
            })
        },
        optimise:()=> {
            let linkIds = [],
                from = $("input[name=optimise-from]").val(),
                to = $("input[name=optimise-to]").val(),
                step = $("input[name=optimise-step]").val();

            $(".optimise-option .selected input[type=hidden]").each((indx, value)=> {
                linkIds.push($(value).val());
            });

            console.log("optimism");
            $.ajax({
                url: "/molvi/optimize",
                data: {
                    "links2stretch": JSON.stringify(linkIds),
                    "from": from,
                    "to": to,
                    "step": step
                },
                success: (data)=> {
                    //console.log(data);
                    //let psurl = "data:image/png;base64,"+ data;
                    //console.log(data);
                    let imgdata = `data:image/png;base64,${data}`;
                    $("#iimmgg").attr('src', imgdata);
                    let win = window.open();
                    win.document.write('<iframe src="' + imgdata  + '" frameborder="0" style="width:100%; height:100%;" allowfullscreen></iframe>');
                },
                error: (data) => {
                    console.error("error in optimizer");
                    document.write(data.responseText);
                }
            })
        },
        closeOptimisation() {
            $("#optimize-links").fadeOut(300);
        },
        openOptimisation() {
            $("#optimize-links").fadeIn(200);
            app.optimisationLoading = true;
            $.ajax({
                url: "/molvi/get-optimise-sources",
                success: (data)=>{
                    app.optimisationLoading = false;
                    let ans = JSON.parse(data);
                    app.optimisers = ans;
                },
                error: (data)=> {
                    app.optimisationLoading = false;
                    console.error("Error while getting optimisers");
                    console.error(data.responseText);
                }
            })
        },
        selectAtomsById(atomList) {
            this.selectedAtomIds = atomList;
            console.log("now selected:");
            console.log(atomList);
        },
        unselectLinks() {
            this.selectedLinkIds = [];
        },
        selectLinkById(id) {
            console.log("selectLinkById("+id+")");
            this.selectedLinkIds = [id];

            engine.build3DFromDoc();
            //engine.buildHtmlFromDoc();
        },

        closeControls() {
            $(".controls").hide();
        },
        openMoveControls(clusterId){
            console.log("open move for: " + clusterId);
            "use strict";

            $("#moveMoleculaId").html(clusterId);
            $('#moleculaMoveControls').show();

            $("#moveControl_x").val(0);
            $("#moveControl_y").val(0);
            $("#moveControl_z").val(0);

            // view.controls.enabled = false
            closeControls();
            $(".control-cluster-position").fadeIn(200);
        },
        openChangeLinkLengthPanel(linkid, oldLength) {
            console.log("openChangeLinkLengthPanel("+linkid+", "+oldLength+")");
            closeControls();
            $(".control-link-length").fadeIn(200);

            $("#linkLengthOld").html(oldLength);
            $("input[name=linkLengthNew]").val(oldLength);
            $("input[name=linkChangeLengthId]").val(linkid);
            view.disableControls();
        },
        editValenceAngle(id, currentValue) {
            console.log("editValenceAngle("+id+", "+currentValue+")");
            $(".controls").hide();
            $(".control-valence-angle").fadeIn(300);

            $(".control-valence-angle .input-id").val(id);
            $(".control-valence-angle .current-value").html(currentValue);
        },
        deleteLink(id4del) {
            console.log("on my way to delete link with id:");
            console.log(id4del);

            app.$delete(app.links, id4del);
            engine.build3DFromDoc();
            engine.buildHtmlFromDoc();

            let links = [];
            Object.keys(app.links).forEach((linkid)=>{
                    links.push({
                        "from": app.links[linkid].atom1,
                        "to": app.links[linkid].atom2
                    })
                }
            );

            $.ajax({
                url: "/molvi/save-links",
                method: "GET",
                data: {
                    "clear": true,
                    "links": JSON.stringify(links)
                },
                success: function (data) {
                    console.log(data);
                    engine.LoadAtomDataFromServer(true);
                },
                error: function (data) {
                    alert("error. c console for details");
                    console.warn(data.responseText);
                }
            });
        },
        deleteDihedralAngle(id){
            console.log('deleteDihedralAngle(' + id + ')');
            $.ajax({
                url: "/molvi/dihedral-angle-delete",
                method: "POST",
                data: {
                    "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                    "id": id
                },
                success(data){console.log(data); app.dihedralAngles=data},
                error(data){console.error(data.responseText);}
            })
        },
        optimizeDihedralAngle(id){
            $.ajax({
                url: "/molvi/dihedral-angle-optimize",
                method: "POST",
                data: {
                    "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                    "id": id
                },
                success(data) {
                    console.log(data);
                },
                error(data) {
                    document.body.innerHTML = data.responseText;
                }
            })
        },
        saveAtomsToActive() {
            // сохранить текущую конфигурацию атомов в активном документе
            $.ajax({
                url: "/molvi/save-to-active",
                method: "POST",
                data: {
                    "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                    "atoms": JSON.stringify(app.atoms)
                },
                success(data) {
                    console.log(data);
                },
                error(data) {
                    document.body.innerHTML = data.responseText;
                }
            })
        }
    },
    watch: {
        atoms: function(newAtoms) {
            engine.build3DFromDoc();
        },
        selectedAtomIds: function(val) {
            engine.selectAtomsById(val);
        }
    },
    mounted: ()=>{
        this.requestAnimationFrame(()=>{
            //app.openOptimisation();
        });

    }
});

function loading_display(ison) {
    if (ison) {
        $(".loading").show();
    } else {
        $(".loading").hide();
    }
}


function editValenceAngle(id, currentValue) {
    $(".controls").hide();
    $(".control-valence-angle").fadeIn(300);

    $(".control-valence-angle .input-id").val(id);
    $(".control-valence-angle .current-value").html(currentValue);
}

class Settings {
    constructor() {
        this.openFileUrl = "/molvi/server/open-file-dialog";
        this.loadActiveFileUrl = "/molvi/get-active-data";
        this.loadMolFileUrl = "/molvi/open-mol-file";
        this.loadDocumentUrl = "/molvi/get-document";
        this.saveDocumentToServerUrl = "/molvi/save-document";
        this.sphereDetalisation = 20;  // количество полигонов при отрисовке сферических объектов
        this.getDocumentsUrl = "/molvi/get-documents"; // запрос документов на сервере
        this.getMolsUrl = "/molvi/get-mol-files"; // запрос .mol файлов на сервере
        this.rotateClusterUrl = "/molvi/rotate-cluster";  // запрос на вращение кластера молекул относительно точки
    }
}
let settings = new Settings(),
    lastId = 0;

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
        //this.id = getId();
        this.documentindex = 0;
    }
}

/**
 * Набор атомов (кластер)
 */
class Cluster {
    constructor() {
        this.atomList = [];
        this.caption = "noname custler";
        //this.id = getId();
    }
}

/**
 * Информация о связи
 */
class Link {
    constructor(fromId, toId, name, value) {
        //this.id = getId();
        this.from = fromId;
        this.to = toId;
        this.name = name;
        this.value = value;
    }
}

class ValenceAngle {
    constructor(id, name, value, atom1Id, atom2Id, atom3Id, link1Id, link2Id) {
        this.id = id;
        this.atom1Id = atom1Id;
        this.atom2Id = atom2Id;
        this.atom3Id = atom3Id;
        this.link1Id = link1Id;
        this.link2Id = link2Id;
        this.name = name;
        this.value = value;
    }
}

/**
 * Документ, хранящий информацию о рабочей области
 */
class MolviDocument {
    constructor() {
        this.links = [];
        this.clusters = [];
        this.valenceAngles = [];
        this.documentName = "no name";

        this.selectedAtomIds = [];  // список выделенных атомов
        this.selectedLinkIds = [];  // список выделенных Link-ов
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

                if (dict.length == 0) {
                    html = "На сервере нет сохранённых документов"
                } else {
                    dict.forEach(function (item) {
                        html += htmlChunk.replace('[+content]', item).replace('[+id]', "file_" + item);
                    });
                }


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
                        var loaded_doc = JSON.parse(data);
                        console.log(loaded_doc)
                        console.log(loaded_doc.atoms);

                        // создание нового документа
                        doc = new MolviDocument();
                        loaded_doc.clusters.forEach(function (lc) {
                            var newCluster = new Cluster();
                            newCluster.caption = lc.caption;
                            newCluster.id = lc.id;
                            doc.clusters.push(newCluster);

                            lc.atoms.forEach(function (la) {
                                var newAtom = new Atom(la.x, la.y, la.z, la.name);
                                newAtom.id = la.id;
                                newAtom.mass = la.mass;
                                newAtom.radius = MolviConf.getAtomRadius(la.name);
                                newAtom.documentindex = la.documentindex;

                                newCluster.atomList.push(newAtom);
                            });
                        });
                        engine.build3DFromDoc();
                        engine.buildHtmlFromDoc();

                        view.closeOpenFileDialog();
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
        let element = $("#openFileDialogMol .selected"),
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
                    'filename': fileName,
                    'clear': deleteold
                },
                error(data) {
                    $("#openFileDialogMol .fileView").html(data.responseText);
                },
                success(data) {
                    // получен json файл с информацией о молекуле
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
        return;
        var ahtml = "",
            mhtml,
            buf,
            html = "";
        doc.clusters.forEach(function(cluster) {
            ahtml = "";
            cluster.atomList.forEach(function (atom) {
                buf = Chunks.atom.replace(/\[\[id]]/g, atom.documentindex);
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

        let linkshtml = "",
            newHtml = "",
            chunk = Chunks.link;
        doc.links.forEach(function (link) {
            newHtml = chunk.replace(/\[FROM]/g, link.from);
            newHtml = newHtml.replace(/\[TO]/g, link.to);
            newHtml = newHtml.replace(/\[ID]/g, link.id);
            newHtml = newHtml.replace(/\[name]/g, link.name);
            newHtml = newHtml.replace(/\[length]/g, link.length);
            newHtml = newHtml.replace(/\[value]/g, link.value);
            linkshtml += newHtml;
        });

        /*let valenceangleshtml = "";

        chunk = Chunks.valenceAngle;

        doc.valenceAngles.forEach(function (angle) {
            newHtml = chunk.replace(/\[title]/g, angle.name);
            newHtml = newHtml.replace(/\[id]/g, angle.id);
            newHtml = newHtml.replace(/\[atom1]/g, angle.atom1Id);
            newHtml = newHtml.replace(/\[atom2]/g, angle.atom2Id);
            newHtml = newHtml.replace(/\[atom3]/g, angle.atom3Id);
            newHtml = newHtml.replace(/\[link1]/g, angle.link1Id);
            newHtml = newHtml.replace(/\[link2]/g, angle.link2Id);
            newHtml = newHtml.replace(/\[value]/g, angle.value);
            valenceangleshtml += newHtml;
        });
        $(".valenceAnglesView").html(valenceangleshtml);*/

        $(".atomsView").html(html);
        $(".linksView").html(linkshtml);

    }

    selectionMaterial(){
        let ans = new THREE.MeshNormalMaterial({ // .MeshPhongMaterial({
            // color: 0xef2500
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
            view.atomMaterials[0] = null;
            view.atomMaterials.splice(0, 1);
        }

        //////////////////// Clusters & atoms ////////////////////////
        view.labels = [];  // clear labels
        let disp = document.getElementById("display");
        while (disp.children.length > 1) {
            disp.children[1].remove();
        }

        for (let key in app.clusters) {
            let cluster = app.clusters[key];
            cluster.atoms.forEach(function (atom_id) {
                let atom = app.atoms[atom_id],
                    radius = MolviConf.getAtomRadius(atom.name),
                    sd = settings.sphereDetalisation,
                    geometry = new THREE.SphereGeometry(radius, sd, sd),
                    material = engine.buildAtomMaterial(atom.name),
                    mesh = new THREE.Mesh(geometry, material),
                    htmllabel = htmlLabels.createLabel();

                mesh.position.x = parseFloat(atom.x);
                mesh.position.y = parseFloat(atom.y);
                mesh.position.z = parseFloat(atom.z);
                view.atomGroup.children.push(mesh);
                view.atomMaterials.push(material);

                htmllabel.setParent(mesh);
                htmllabel.setHTML(atom.name + atom.documentindex);
//                console.log(atom);
                view.labels.push(htmllabel);

                disp.appendChild(htmllabel.element);

            });
        }

        /////////////////////// LINKS ///////////////////////////////
        //удаление старых Mesh'эй
        while (view.linkGroup.children.length > 0) {
            view.linkGroup.children[0] = null;
            view.linkGroup.children.splice(0, 1);
        }
        //создание Mesh'ей
        for (let link_id in app.links) {
            let link = app.links[link_id],
                atom1 = null,
                atom2 = null;

            /*for (let cluster_id in app.clusters) {
                let cluster = app.clusters[cluster_id];
                for (let atom_indx in cluster.atoms) {
                    let atom_id = cluster.atoms[atom_indx],
                        atom = app.atoms[atom_id];
                    if (atom_id === link.atom1) {
                        atom1 = atom;
                    }
                    if (atom.id === link.atom2) {
                        atom2 = atom;
                    }
                }
            }*/
            if (app.atoms.hasOwnProperty(link.atom1)) {
                atom1 = app.atoms[link.atom1];
            }
            if (app.atoms.hasOwnProperty(link.atom2)) {
                atom2 = app.atoms[link.atom2];
            }

            if (atom1 == null) {
                console.error("atom 1 not finded!");
                return;
            }
            if (atom2 == null) {
                console.error("atom 2 not finded!");
                return;
            }

            let lineColor = 0xf6ff0f;
            if (app.selectedLinkIds.includes(link_id)) {
                lineColor = 0xff0000;
            }

            let lineMesh = view.buildLineMesh(atom1.x, atom1.y, atom1.z, atom2.x, atom2.y, atom2.z, lineColor);
            view.linkGroup.add(lineMesh);

        }

        ////////////////////// SELECTED ///////////////////////
        while (view.outlinesGroup.children.length > 0) {
            view.outlinesGroup.children[0] = null;
            view.outlinesGroup.children.splice(0, 1);
        }

        app.selectedAtomIds.forEach(function (id) {
            let satom = app.atoms[id],
                outlineMaterial = new THREE.MeshBasicMaterial({color: 0x8A00BD, side: THREE.BackSide}),
                r = MolviConf.getAtomRadius(satom.name) * 1.2,
                sd = settings.sphereDetalisation,
                outlineGeometry = new THREE.SphereGeometry(r, sd, sd),
                outline = new THREE.Mesh(outlineGeometry, outlineMaterial);

            outline.position.set(satom.x, satom.y, satom.z);
            //outline.scale.multiplyScalar(1.1);
            view.outlinesGroup.add(outline);
        })
    }

    /**
     * Показать сообщение для пользователя
     * (вызов без аргументов спрячет поле сообщений)
     */
    userMessage(message) {
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
        let pointedAtoms = [];
        console.log(11);

        if (view.highlights.length === 1) {
            let point = view.highlights[0].point, // точка пересечения raycaster'a с объектом
                r = 0,
                owners = [],
                sx, sy, sz;
            // вычисление того, какому объекту принадлежит эта точка
            Object.keys(app.clusters).forEach((key)=>{
                let cluster = app.clusters[key];

                cluster.atoms.forEach(function (atomid) {
                    let atom = app.atoms[atomid];
                    r = MolviConf.getAtomRadius(atom.name);

                    sx = (point.x - atom.x)*(point.x - atom.x);
                    sy = (point.y - atom.y)*(point.y - atom.y);
                    sz = (point.z - atom.z)*(point.z - atom.z);

                    if (Math.sqrt(sx + sy + sz) <= r) {
                        console.log(atom.name);
                        owners.push(atom);
                    }
                });
            });

            owners.forEach(function (owner) {
                engine.selectAtomById(owner.documentindex);
                pointedAtoms.push(owner.documentindex);
            });
        }

        // действия, зависящие от режима управления
        if (engine.controlMode === "rotate") {  // вращение кластера
            if (doc.selectedAtomIds.length >= 1) {
                $("#transformRotate>.origin").val(doc.selectedAtomIds[0]);
                engine.userMessage();
                if (doc.selectedAtomIds.length > 1) {
                    console.error("zdes tvoritsia mistika!");
                }
                $("#transformRotate").show();
                view.disableControls();
                window.requestAnimationFrame(function () {
                    $("#tr_dx").val(0.0);
                    $("#tr_dy").val(0.0);
                    $("#tr_dz").val(0.0);
                    $("#tr_dx").focus();
                    $("#tr_dx").select();
                });
            }
        } else if (engine.controlMode === "link") { // создание связи
            engine.linkCreationSource = doc.selectedAtomIds;
            engine.linkCreation();
            //console.log(doc.selectedAtomIds);
            //engine.linkCreationSource
        } else if (engine.controlMode === "dihedral creation") {
            if (pointedAtoms.length >= 1) {
                if (!dihedralAngleCreator.collected.includes(pointedAtoms[0])) {
                    dihedralAngleCreator.addAtom(pointedAtoms[0]);
                }
            }
        }



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

    startLinkCreationHtml() {
        engine.linkCreationSource = [];
        engine.unselectAtoms();
        engine.controlMode = 'link';
        engine.linkCreation();
    }

    /**
     * Создание связи
     * @param {Array} ids массив id для создания связи [] или [id]
     */
    linkCreation(){
        // не выбрано ниодного атома
        if (engine.linkCreationSource.length == 0) {
            engine.userMessage("Выберите атом #1");

        } else if(engine.linkCreationSource.length == 1) {
            engine.userMessage("Выберите атом #2");
        }

        //ids содержит что-то
        if (this.linkCreationSource.length == 2) {
            engine.userMessage();
            let atom1 = null,
                atom2 = null;

            doc.clusters.forEach(function (cluster) {
                cluster.atomList.forEach(function (atom) {

                })
            });

            let newLink = new Link(this.linkCreationSource[0], this.linkCreationSource[1], "new linkk", 0);
            doc.links.push(newLink);
            $.ajax({
                url: '/molvi/create-link',
                method: 'POST',
                data: {
                    "atom1": this.linkCreationSource[0],
                    "atom2": this.linkCreationSource[1],
                    "csrfmiddlewaretoken": $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    engine.LoadAtomDataFromServer(true);
                },
                error: function (data) {
                    console.error("error while link creation: " + data.responseText);
                }
            });

            engine.controlMode ='none';
//            engine.buildHtmlFromDoc();
//            engine.build3DFromDoc();
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
        engine.controlMode = modeName;

        if(modeName === 'line'){
            $("#icon_modeLineUnselected").hide();
            $("#icon_modeLineSelected").show();
            this.linkCreation([]);
        }
    }

    LoadAtomDataFromServer(deleteold) {
        let url = settings.loadActiveFileUrl;

        loading_display(true);

        $.ajax({
            url: url,
            success: function(data){
                // $(".atomsView").html(data); !!!!!
//              console.log("LoadAtoms: data loading OK")
                engine.buildAtomData(data, deleteold);
//                console.log(data);
            },
            error: function(data) {
                $(".atomsView").html(data.responseText);
                console.log("ERROR");
                console.log(data);
            },
            complete: function () {
                loading_display(false);
            }
        })
    }

    LoadMolFromServer(deleteold) {

    }

    /**
     *
      * @param id
     */
    selectAtomById(id, clear=false) {
        // принудительные значения clear
        if (engine.controlMode == 'line') {
            clear = false;
        } else if (engine.controlMode == 'none'){
            clear = true;
        }

        if (clear) {
            doc.selectedAtomIds = [];
        }
        doc.selectedAtomIds.push(id);
        engine.build3DFromDoc();
    }

    selectAtomsById(ids, clear=true) {
        if (clear) {
            doc.selectedAtomIds = [];
        }

        ids.forEach(function (id) {
            doc.selectedAtomIds.push(id);
            engine.build3DFromDoc();
        })
    }

    /**
     * Снять выделение со всех атомов
     */
    unselectAtoms() {
        doc.selectedAtomIds = [];
        engine.build3DFromDoc();
    }

    selectLinkById(id) {
        console.log("selectLinkById("+id+")");
        doc.selectedLinkIds = [];
        doc.selectedLinkIds.push(id);

        engine.build3DFromDoc();
        //engine.buildHtmlFromDoc();
    }

    selectLinksById(ids) {
        doc.selectedLinkIds = [];

        ids.forEach(function (id) {
            let iid = parseInt(id);
            doc.selectedLinkIds.push(iid);
        });

        engine.build3DFromDoc();
    }

    selectLinkByIds(id1, id2) {
        var thisLink = null;
        doc.links.forEach(function (link) {
            if (((link.from === id1) && (link.to === id2)) ||
                ((link.fomr === id2) && (link.to === id1)))
            {
                thisLink = link;
            }
        });
        if (thisLink != null) {
            engine.selectAtomById(thisLink.id);
        }
    }

    unselectLinks() {
        doc.selectedLinkIds = [];
    }

    deleteLink(id4del) {
        console.log(id4del);
        console.log("this kind of deleteLink is deleted. Sry for it.");
    }

    /**
     * Создание объектов для содержания информации об атомах
     * @param jsonString информация об атомах
     * @param deleteOld true => удалить все старые атомы
     */
    buildAtomData(jsonString, deleteOld){
        //создание рабочего документа (хранит всю рабочую инфу)
        // decide how to do with old data
        deleteOld = true;
        if (deleteOld) {
            doc = new MolviDocument();

            app.clusters = {};
            app.atoms = {};
        }
        let docData = JSON.parse(jsonString),
            clusterN = count(app.clusters),
            newCluster = {
                caption: "Кластер " + clusterN,
                atoms: []
            };

        // список атомов храняться на уровне документа
        app.atoms = docData.atoms;
        app.clusters = docData.clusters;
        // список связей
        app.links = docData.links;
        app.valenceAngles = docData["valence_angles"];
        console.log(docData);
        doc.documentName = docData["name"];

        let atar = JSON.parse(jsonString);
        let satoms = docData["atoms"],
            atomlist = {};

        // legacy
        /*
        satoms.forEach(function(item, indx){
            let x = parseFloat(item['x']),
                y = parseFloat(item['y']),
                z = parseFloat(item['z']),
                id = parseInt(item['id']),
                mass = parseFloat(item['mass']),
                name = item['name'],
                documentindex = parseInt(item['documentindex']),
                newAtom = new Atom(x, y, z, name);
                newAtom.id = id;
                newAtom.mass = mass;
                newAtom.documentindex = documentindex;
            atomlist[id] = newAtom;
        });

        docData["clusters"].forEach(function (scluster) {
            let newCluster = new Cluster();
            newCluster.id = scluster["id"];
            newCluster.caption = scluster["caption"];
            doc.clusters.push(newCluster);

            scluster.atoms.forEach(function (atomid) {
                newCluster.atomList.push(atomlist[atomid]);
            });
        });

        docData["links"].forEach(function (link) {
            let newLink = new Link(link["atom1"], link["atom2"], link["name"], link["value"]);
            newLink.id = link["id"];
            newLink.length = link["length"];
            doc.links.push(newLink);
        });

        docData["valence_angles"].forEach(function (angle) {
            let id = angle["id"],
                name = angle["name"],
                a1 = angle["atom1"],
                a2 = angle["atom2"],
                a3 = angle["atom3"],
                link1 = angle["link1"],
                link2 = angle["link2"],
                value = parseFloat(angle["value"]).toFixed(2),
                newVA = new ValenceAngle(id, name, value, a1, a2, a3, link1, link2);

            doc.valenceAngles.push(newVA);

        });*/
        app.valenceAngles = docData["valence_angles"];

        app.dihedralAngles = docData["dihedral_angles"];

        engine.buildHtmlFromDoc();
        engine.build3DFromDoc();

        //reset to default view
        //view.resetCamera();
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
                alert("Ошибка при открытии файла");
                console.log("open file error: " + data.toString())
            }
        })
    }

    /**
     * Открыть элементы управления для переноса кластера
     * @param clusterId id кластера, который требуется перенести
     */
    openMoveControls(clusterId){
        "use strict";

        $("#moveMoleculaId").html(clusterId);
        $('#moleculaMoveControls').show();

        $("#moveControl_x").val(0);
        $("#moveControl_y").val(0);
        $("#moveControl_z").val(0);

        // view.controls.enabled = false
        closeControls();
        $(".control-cluster-position").fadeIn(200);
    }

    /**
     * Закрыть элементы управления для переноса кластера
     */
    closeMoveControls(xhift, yshift, zshift){
        view.controls.enabled = true;
        $('#moleculaMoveControls').hide()
    }

    doMoleculaMove(axis, value) {
        let xshift = "0",
            yshift = "0",
            zshift = "0",
            id = $("#moveMoleculaId").html();

        if (axis === "all") {
            xshift = $("#moveControl_x").val();
            yshift = $("#moveControl_y").val();
            zshift = $("#moveControl_z").val();
        } else if (axis === "x") {
            xshift = value;
        } else if (axis === "y") {
            yshift = value;
        } else if (axis === "z") {
            zshift = value;
        }
        xshift = parseFloat(xshift);
        yshift = parseFloat(yshift);
        zshift = parseFloat(zshift);
        id = parseInt(id);

        if (isNaN(xshift) || isNaN(yshift) || isNaN(zshift)){
            console.log("Parse error!");
            $("#moleculaMoveControls").hide();
            return;
        }
        console.log('doMoleculaMove, id: ' + id);
        let cluster = null;
        if (app.clusters.hasOwnProperty(id)) {
            cluster = app.clusters[id];
        }
        if (cluster === null) {
            console.error("No cluster found. with id: " + id.toString());
            return;
        } else {
            for (let atom_indx in cluster.atoms) {
                let atom_id = cluster.atoms[atom_indx],
                    atom = app.atoms[atom_id];

                atom.x += xshift;
                atom.y += yshift;
                atom.z += zshift;
            }
        }
        engine.closeMoveControls();

        $.ajax({
            url: "/molvi/edit-cluster-move",
            data: {
                "cluster": id,
                "x": xshift,
                "y": yshift,
                "z": zshift
            },
            success: function (data) {
                console.log(data);
                engine.LoadAtomDataFromServer(true);
            },
            error: function (data) {
                alert("Error! c console for more in4");
                console.warn(data.responseText);
            }
        });

        //engine.buildHtmlFromDoc();
        //engine.build3DFromDoc();
    }

    executeAutoTrace() {
        let radius = 1.6,
            re = document.getElementById('traceRange').value;
        radius = parseFloat(re);
        if (isNaN(radius)) {
            console.log("Error in parse int");
            alert('Введите корректное значение длины автотрассировки');
            return;
        }

        //удаление старых связей
        /*while(doc.links.length > 0) {
            doc.links[0] = null;
            doc.links.splice(0, 1);
        }*/
        let newLinks = [];

        //let rmin,
          //  numberj;
        for (let cluster1_id in app.clusters) {
            let cluster1 = app.clusters[cluster1_id];
            for (let cluster2_id in app.clusters) {
                let cluster2 = app.clusters[cluster2_id];
                for (let indx1 in cluster1.atoms) {
                    let atom1_id = cluster1.atoms[indx1],
                        atom1 = app.atoms[atom1_id];
                    for (let indx2 in cluster2.atoms) {
                        let atom2_id = cluster2.atoms[indx2],
                            atom2 = app.atoms[atom2_id];
                           if (atom1_id === atom2_id) {
                           } else {
                               let r1 = Math.pow(atom1.x - atom2.x, 2),
                                   r2 = Math.pow(atom1.y - atom2.y, 2),
                                   r3 = Math.pow(atom1.z - atom2.z, 2),
                                   r = Math.sqrt(r1 + r2 + r3);

                               if(r <= radius) {
                                   let newlink = {
                                       from: atom1_id,
                                       to: atom2_id
                                   };
                                   newLinks.push(newlink);
                               }
                           }
                   }
               }
           }
        }

        //ревизия созданных связей
        newLinks.forEach(function(link1) {
            newLinks.forEach(function(link2, ind) {
                if ((link1.from === link2.from) && (link1.to === link2.to)) //это одна и та же связь
                    return;

                if ((link2.to === link1.from) && (link2.from === link1.to)) { // связи разные, но одинаковые
                    newLinks.splice(ind, 1);
                }
            });
        });

        $.ajax({
            url: "/molvi/save-links",
            method: "GET",
            data: {
                "clear": true,
                "links": JSON.stringify(newLinks)
            },
            success: function (data) {
                console.log(data);
                engine.LoadAtomDataFromServer(true);
            },
            error: function (data) {
                alert("error. c console for details");
                console.warn(data.responseText);
            }
        });

        //engine.buildHtmlFromDoc();
        //engine.build3DFromDoc();
    }

        rotateCluster(centerAtomId = null, dx = null, dy = null, dz = null) {
        if (centerAtomId == null) {
            engine.unselectAtoms();

            engine.userMessage("Выберите атом (центр вращения)");
            engine.controlMode = "rotate";
        } else {
            // уже выбран атом, вокруг которого надо крутить молекулу

            $("#transformRotate>.dx>input").val("0.0");
            $("#transformRotate>.dy>input").val("0.0");
            $("#transformRotate>.dz>input").val("0.0");
        }

    }

    /**
     * Вызов вращения кластера из html страницы
     */
    rotateClusterFromHtml() {
        var cluster = null,
            originId = parseInt($("#rotateOrigin").val()),
            ox = 0,
            oy = 0,
            oz = 0,
            atoms = [];

        //цикл по всем кластерам
        Object.keys(app.clusters).forEach((key)=>{
            let ccluster = app.clusters[key];

            ccluster.atoms.forEach(function (atom) {
                if (atom === originId) {
                    cluster = ccluster;
                    ox = app.atoms[atom].x;
                    oy = app.atoms[atom].y;
                    oz = app.atoms[atom].z;
                }
            });
        });
        /*doc.clusters.forEach(function (ccluster) {
            ccluster.atomList.forEach(function (atom) {
                if (atom.id == originId) {
                    cluster = ccluster;
                    ox = atom.x;
                    oy = atom.y;
                    oz = atom.z;
                }
            });
        });*/

        if (cluster != null) {
            cluster.atoms.forEach(function (atom) {
                atoms.push({
                    "x": app.atoms[atom].x,
                    "y": app.atoms[atom].y,
                    "z": app.atoms[atom].z
                });
            });
            let ax = parseFloat($("#tr_dx").val()),
                ay = parseFloat($("#tr_dy").val()),
                az = parseFloat($("#tr_dz").val()),
                atoms_json = JSON.stringify(atoms);

            $.ajax({
                url: settings.rotateClusterUrl,
                data: {
                    "points": atoms_json,
                    "origin": JSON.stringify({"x": ox, "y": oy, "z": oz}),
                    "ax": ax,
                    "ay": ay,
                    "az": az
                },
                error(data) {
                    console.error($("body").html(data.responseText));
                },
                success(data) {
                    console.log(cluster);
                    let ans = JSON.parse(data);
                    ans.forEach(function (a, indx) {
                        /*cluster.atomList[indx].x = a[0];
                        cluster.atomList[indx].y = a[1];
                        cluster.atomList[indx].z = a[2];*/
                        app.atoms[cluster.atoms[indx]].x = a[0];
                        app.atoms[cluster.atoms[indx]].y = a[1];
                        app.atoms[cluster.atoms[indx]].z = a[2];
                    });
                    engine.build3DFromDoc();
                    engine.buildHtmlFromDoc();
                    engine.closeRotationHtml();
                    app.saveAtomsToActive();
                }

            });
        }
    }

    closeRotationHtml() {
        $("#transformRotate").hide();
        engine.controlMode = 'none';
        view.enableControls();
        engine.unselectAtoms();
    }

    saveAction(){
        // выбрано сохранение как .mol
        if ($("#save-mol-file").hasClass("selected")) {
          this.saveMolFileToServer();
        } else if ($("#save-document").hasClass("selected")) {
            // выбрано сохранение документа во внутреннем формате
            this.saveDocumentToServer();
        }
    }

    saveMolFileToServer() {
        $.ajax({
            url: "/molvi/save-mol-file",
            method: "POST",
            data: {
                "filename": JSON.stringify($("#saveFileName").val()),
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            },
            error: function (data) {
                alert(data.responseText);
            }
        })
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
            };
            //заполнение атомов кластера
            cluster.atomList.forEach(function (atom) {
                var myatom = {
                    x: atom.x,
                    y: atom.y,
                    z: atom.z,
                    name: atom.name,
                    mass: atom.mass
                };
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
                engine.userMessage("Ошибка при сохранении документа на сервер");
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
        this.atomMaterials = [];
        this.outlinesGroup = new THREE.Group();
        this.outlinesGroup.name = "outlines group";
        this.engine = null;
        this.renderer = new THREE.WebGLRenderer({alpha: true});
        this.camera = null;
        this.controls = null;
        this.viewHeight = 50;
        this.viewWidth = 50;

        // "рабочие" группы
        this.highlights = [];  // Array<Three.Mesh>
        this.selected = [];  // Array<Three.Mesh>

        this.labels = [];

        this.container = false;  // container of 3d content (usualy div)

    }

    init() {
        "use strict";
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

        let aspect = width / height,
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

        htmlLabels.setContainer(document.getElementById(hostid));
    }

    static paintGL() {
        requestAnimationFrame(MolviView.paintGL);

        //this.controls.update();

        view.handleSelection();

        view.renderer.render(view.scene, view.camera);

        for (let i=0; i < view.labels.length; i++) {
            view.labels[i].updatePosition();
        }
    }

    buildScene() {
        view.scene.background = new THREE.Color(0x000000);
        view.scene.children.splice(0, this.scene.children.length);

        //добавить свет
        let light1 = new THREE.DirectionalLight(0xffffff, 0.3),
            light2 = new THREE.AmbientLight(0xffffff, 0.5);

        view.lightGroup.add(light1);
        view.lightGroup.add(light2);
        view.scene.add(this.lightGroup);

        //добавить вспомогательные элементы
        let helper = new THREE.AxesHelper(22),
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
        let array = new Float32Array([x1, y1, z1, x2, y2, z2]),
            color = new THREE.Color(colorHex),
            material = new MeshLineMaterial({
                color: color,
                opacity: 1,
                lineWidth: 0.03
            });

        let temp = new MeshLine();
        temp.setGeometry(array);
        let geom = temp.geometry;

        let mesh = new THREE.Mesh(geom, material);
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
        console.log("controls On");
    }
    disableControls(){
        view.controls.enabled = false;
        console.log("controls OFF");
    }

    click() {
        console.log(1);
    }
    /**
     * Обработка наведения на элементы
     */
    handleSelection(){
        view.raycaster.setFromCamera(view.mousePosition, view.camera);
        //console.log(mousePosition);

        let atoms = view.atomGroup.children,
            links = view.linkGroup.children,
            intersects = view.raycaster.intersectObjects(atoms),
            linkInter = view.raycaster.intersectObjects(links);

        //console.log(linkInter);
        //console.log(links)


        //var highlighted = view.highlights;
        view.highlights = [];

        for (let i = 0; i < atoms.length; i++){
            atoms[i].material =  view.atomMaterials[i]; //engine.buildAtomMaterial(atoms[i].name);
        }

        // выбор всех элементов, надо которыми наведена мышка///////
        /*
        for (var i = 0; i < intersects.length; i++) {
            intersects[i].object.material = engine.selectionMaterial();
            highlighted.push(intersects[i]);
        }*/
        ////////////////////////////////////

        // выбор только ближайшего//////////
        if (intersects.length > 0) {
            view.highlights.push(intersects[0]);
        }

        for (let i = 0; i < intersects.length; i++) {
            if (view.highlights.length === 0) {
                view.highlights.push(intersects[i]);
            }
            if (intersects[i].distance < view.highlights[0].distance) {
                view.highlights.splice(0, 1);
                view.highlights.push(intersects[i]);
            }
        }
        ///////////////////////////////////

        // подсветка выделенного

        for (let i = 0; i < view.highlights.length; i++) {
            view.highlights[i].object.material = engine.selectionMaterial();
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
        } else if (mode === 'plusmol') {
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

function selectPanel(panelName) {
    $(".viewPanel").hide();
    $(".selector").removeClass("checked");

    $("#panel"+panelName).fadeIn(500);
    $("#selector"+panelName).addClass("checked");
}

function openChangeLinkLengthPanel(linkid, oldLength) {
    closeControls();
    $(".control-link-length").fadeIn(200);

    $("#linkLengthOld").html(oldLength);
    $("input[name=linkLengthNew]").val(oldLength);
    $("input[name=linkChangeLengthId]").val(linkid);
    view.disableControls();
}

function closeChangeLinkLengthPanel(){
    $("#linkChangeLengthControls").hide();
    view.enableControls();
}


function changeLinkLength() {
    let id = $("input[name=linkChangeLengthId]").val(),
        length = $("input[name=linkLengthNew]").val();

    loading_display(true);

    $.ajax({
        url: "edit-link-set-length",
        data: {
            "link": id,
            "length": length
        },
        success: function (data) {
            console.log(data);
            engine.LoadAtomDataFromServer(true);
        },
        error: function (data) {
            alert("Error c console 4 more in4");
            loading_display(false);
        }

    });
}

function openLinkRotationPanel(id, from, to) {
    console.log("OpenLinkRotationPanel");
    console.log(id, from, to);
    $(".viewPanel").hide();
    $("#linkRotationPanel").fadeIn(500);

    $("input[name=linkRotation_link]").val(id);
    $("input[name=linkRotation_atom1]").val(from);
    $("input[name=linkRotation_atom2]").val(to);

    view.disableControls();
}

function closeLinkRotationPanel() {
    $("#linkRotationPanel").hide();
    $(".selector:first-child").click();

    view.enableControls();
}

function linkRotationHighlight(atomn) {
    $(".dont-move").removeClass("selected");
    $(".dont-move:nth-child(" +atomn+")").addClass("selected");

    let aid = $("#linkRotationPanel .selected").html();
    if (aid === "A1") {
        engine.selectAtomById($("input[name=linkRotation_atom1]").val());
    } else {
        engine.selectAtomById($("input[name=linkRotation_atom2]").val());
    }

    console.log(aid);
}

function doLinkRotation() {
    let link = $("input[name=linkRotation_link]").val(),
        originAtom = 0,
        degrees = $("input[name=linkRotation_degrees]").val(),
        aid = $("#linkRotationPanel .selected").html();

    if (aid === "A1") {
        originAtom = $("input[name=linkRotation_atom1]").val();
    } else {
        originAtom = $("input[name=linkRotation_atom2]").val();
    }

    $.ajax({
        url: "/molvi/rotate-cluster-around-link",
        data: {
            "link": link,
            "origin-atom": originAtom,
            "degrees": degrees
        },
        success: function (data) {
            console.log(data);
            closeLinkRotationPanel();
            engine.LoadAtomDataFromServer(true);
        },
        error: function (data) {
            alert("Error! c details in console");
            console.warn(data.responseText);
            closeLinkRotationPanel();
        }
    })
}

function buildValenceAngles() {
    loading_display(true);
    $.ajax({
        url: "/molvi/valence-angles-autotrace",
        success: function (data) {
            console.log(data);
            engine.LoadAtomDataFromServer(true);
        },
        error: function (data) {
            alert(data.responseText);
            loading_display(false);
        }
    })
}

function deleteValenceAngle(id) {
    $.ajax({
        url: "/molvi/valence-angles-delete",
        data: {
            "id": id
        },
        success: function (data) {
            console.log(data);
        },
        error: function (data) {
            alert(data.responseText);
        }
    });
}


let engine = new MolviEngine(),
    view = new MolviView(),
    doc = new MolviDocument();


function doEditValenceAngle() {
    let id = $(".control-valence-angle .input-id").val(),
        cur_angle =  $(".control-valence-angle .current-value").html(),
        inp_angle = $(".control-valence-angle .input-angle").val(),
        delta_deg = parseFloat(inp_angle) - parseFloat(cur_angle),
        delta_rad = delta_deg / 180.0 * Math.PI,
        csrf_token = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
        url: "/molvi/valence-angles-change",
        method: "POST",
        data: {
            id: parseFloat(id),
            angle: delta_rad,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (data) {
            console.log("doEditValenceAngle: " + data);
            engine.LoadAtomDataFromServer(true);
        },
        error: function (data) {
            console.error(data.responseText);
            alert("Error! C console 4 in4, pls.");
        }
    });
}



let htmlLabels = {
    x: 1,
    y: 2,
    container: undefined,  // html element to display htmlLabels
    setContainer: function (arg) {
            this.container = arg;
        },
    createLabel: function () {
        let div = document.createElement('div');
        div.className = 'html-label';
        div.innerHTML = "sVETA";

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

                let coords2d = this.get2DCoords(this.position, view.camera);
                this.element.style.left = coords2d.x + 'px';
                this.element.style.top = coords2d.y + 'px';
            },
            get2DCoords: function (position, camera) {
                let vector = position.project(camera);
                vector.x = (vector.x + 1)/2 * thisLabel.container.clientWidth;
                vector.y = -(vector.y - 1)/2 * thisLabel.container.clientHeight;
                return vector;
            }
        }
    }

};

function closeControls() {
    $(".controls").hide();
}

let dihedralAngleCreator = {
    collected: [],  // атомы для создания двугранного угла
    addAtom: function (id) {
        // adding atom for dihedral angle creation
        this.collected.push(id);
        let msg = "Выбрано атомов " + this.collected.length + "/4";
        $(".dihedralAngles .messages .text").html(msg);

        if (this.collected.length >= 4) {
            console.log(this.collected);

            $.ajax({
                url: "/molvi/dihedral-angle-create",
                method: "POST",
                data: {
                    "atoms": JSON.stringify(this.collected),
                    "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
                },
                success(data) {
                    console.log(data);
                    app.dihedralAngles = data;
                },
                error(data) {
                    alert("Не удалось создать двугранный угол: " + data.responseText);
                    console.warn(data.responseText);
                }
            });

            this.collected = [];
            this.stop()
        }
    },
    start: function () {
        this.collected = [];
        engine.unselectAtoms();
        $(".dihedralAngles .messages").show();
        $(".dihedralAngles .messages .text").html("Выбрано атомов: 0/4");
        engine.controlMode = "dihedral creation";
        app.controlMode = 'dihedral creation';
    },
    stop: function () {
        $(".dihedralAngles .messages").hide();
        app.controlMode = 'idle';
    }
};


$(document).ready(function(){
    engine.view = view;
    view.engine = engine;
    MolviEngine.instance = engine;
    MolviView.instance = view;

    engine.userMessage();

    engine.selectMode("none");
    //добавление обработчиков
    let display = document.getElementById("display");
    display.addEventListener("mousemove",  MolviEngine.onMouseMove, false);
    display.addEventListener("mousedown",  MolviEngine.onMouseDown, false);

    view.init();

    //LoadAtoms(true);

    let inputElement = document.getElementById('traceRange');
    inputElement.onkeypress = engine.autoTraceKeyPressed;
    inputElement.value = 1.6;

    //загрузить активный файл с сервера
    engine.LoadAtomDataFromServer(true);


    selectPanel("DihedralAngles");

    console.log(htmlLabels.createLabel());

    closeControls();

    $("#optimize-button").click(()=>{
        app.openOptimisation();
    });
});
