/*global
    THREE
*/
import * as THREE from "./three";

var openFileUrl = "/molvi/cgi-bin/openFileDialog.py"

var camera, scene, renderer, viewWidth, viewHeight;
var raycaster, mousePosition;  // объект для выбора мышкой
var controls;
var light1 = new THREE.DirectionalLight(0xffffff, 0.3),
    light2 = new THREE.AmbientLight(0xffffff, 0.5);
//var atoms = [];
var atomMaterial = []
var highlighted = [];
var selectedAtoms = [];
var selectedIds = [];
var lines = [];
var controlMode = "none";
var links = [],
    highlightedLinks=[];

var outlines = [], // обведение контуров
    outlinesGroup;



function buildAtomMaterial(atomName){
    var ans = new THREE.MeshPhongMaterial({
        color: MolviConf.getAtomColor(atomName),
        wireframe: false
    });
    return ans;
}

var highlightedMaterial = new THREE.MeshNormalMaterial(),
    selectionMaterial = new THREE.MeshPhongMaterial({
        color: 0xff0000
    }),
selectionLinkMaterial=new MeshLineMaterial({
    color: new THREE.Color(0xff0000),
    opacity: 1,
    lineWidth: 0.03
}),
linkMaterial=new MeshLineMaterial({
    color: new THREE.Color(0xf6ff0f),
    opacity: 1,
    lineWidth: 0.03
}),
spehereDetalisation = 20
//atomMaterial = new THREE.MeshNormalMaterial();

var lightGroup,
    atomGroup,
    helpGroup,
    linkGroup;

var linkList = [],
    atomList = []

var linkChunk = `
    <div class="link" id="link_0" onmouseover="highlightLink([ID])" onmouseout="highlightLink()">
        <div class='cell'>
            <span>[FROM]</span><span> - </span><span>[TO]</span>
        </div>
        <div class="deleteLink cell" title="delete link" onclick="deleteLink([ID])">x</div>
    </div>
`,
    atomViewChunk = `
    <div class="atomView" onclick="selectAtom([[id]])" id="atomView_[[id]]">
        <div class="id">[[id]]: </div>
        <div class="name">[[name]]</div>
        <div class="devider"></div>
        <div class="x" contenteditable>x: [[x]]</div>
        <div class="y" contenteditable>y: [[y]]</div>
        <div class="z" contenteditable>z: [[z]]</div>
    </div>
`,
    moleculaViewChunk = `
    <div class="moleculaView">
        <div class="title">
            <span>[[title]] </span><u class='move' onclick='openMoveControls([[id]])'>переместить</u>
        </div>
        <div class="moleculaData">
            [[data]]
        </div>
    </div>
    `

function highlightLink(index){
    
    for(var i=0;i<linkGroup.children.length;i++){
        linkGroup.children[i].material=linkMaterial;
    }
    if(index != undefined){
        linkGroup.children[index].material=selectionLinkMaterial;
    }
    
}

function addLight() {
    scene.add(light1);
    scene.add(light2);
    var helper = new THREE.AxesHelper(22);
    var grid = new THREE.GridHelper(10, 10);
    scene.add(grid);
    scene.add(helper);
}

function buildScene(){
    //добавить свет
    scene.children.splice(0, scene.children.length);

    lightGroup = new THREE.Group();
    lightGroup.name = "lightGroup";
    lightGroup.add(light1);
    lightGroup.add(light2);
    scene.add(lightGroup);

    //добавить вспомогательные элементы
    var helper = new THREE.AxesHelper(22),
        grid = new THREE.GridHelper(10, 10);
    helpGroup = new THREE.Group();
    helpGroup.name = "helpGroup";
    helpGroup.add(grid);
    helpGroup.add(helper);
    scene.add(helpGroup);

    //добавить молекулы
    atomGroup = new THREE.Group();
    atomGroup.name = "atomGroup";
    /*for (var i = 0; i < atoms.length; i++) {
        //var aG = new THREE.SphereGeometry(0.3, spehereDetalisation, spehereDetalisation),
        //    am = new THREE.Mesh(aG, atomMaterial);
        atomGroup.add(atoms[i]);
    }*/
    scene.add(atomGroup);

    //добавить связи между молекулами
    linkGroup = new THREE.Group();
    linkGroup.name = "linkGroup";
    scene.add(linkGroup);

    //добавить объекты для выделения
    outlinesGroup = new THREE.Group();
    outlinesGroup.name = "outlines group";
    scene.add(outlinesGroup);
}

function initGL(host, width, height){
    viewWidth = width;
    viewHeight = height;

    var aspect = width / height,
        host = document.getElementById(host);
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    //camera = new THREE.OrthographicCamera(-10, 10, -10, 10, 0.1, 100)
    camera.position.z = 3;

    controls = new THREE.OrbitControls(camera);
    raycaster = new THREE.Raycaster();
    mousePosition = new THREE.Vector2();


    renderer = new THREE.WebGLRenderer({alpha: true});
    renderer.setClearColor(0xff0000, 0);
    renderer.setSize(width, height);

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    addLight();

    var geometry = new THREE.SphereGeometry( 1, spehereDetalisation, spehereDetalisation);
    var material = new THREE.MeshPhongMaterial({
        //wireframe: true,
        color: 0x00ff00,
        specular: 0x111111
    });
    var sphere = new THREE.Mesh( geometry, material );
    
    
    host.appendChild(renderer.domElement);
}

function paintGL(){
    requestAnimationFrame(paintGL);

    controls.update();

    handleSelection();
    
    renderer.render(scene, camera);
}

function handleSelection(){
    raycaster.setFromCamera(mousePosition, camera);
    //console.log(mousePosition);

    var atoms = atomGroup.children,
        intersects = raycaster.intersectObjects(atoms);
        

    highlighted = []
    for (var i = 0; i < atoms.length; i++){
        atoms[i].material = atomMaterial[i];
    }

    for (var i = 0; i < intersects.length; i++) {
        intersects[i].object.material = highlightedMaterial;
        highlighted.push(intersects[i]);
    }

    // изменение материала выделенных атомов
    /*for (var i = 0; i < selectedAtoms.length; i++) {
        selectedAtoms[i].material = selectionMaterial;
    }*/
}

function userMessage(message) {
    "use strict";
    if (!message){
        $("#infoMessageField").hide();
    } else {
        $("#infoMessageText").html(message);
        $("#infoMessageField").show();
    }
}

class WLink {
    constructor(from, to){
        this.from = from;
        this.to = to;
    }
}

class WAtom{
    constructor(x, y, z, name){
        this.x = x;
        this.y = y;
        this.z = z;
        this.name = name;
    }
}

class WMolecula {
    constructor(title) {
        this.title = title
        this.atoms = [] // ids of atoms in molecula
    }
}

class WDocument{
    


    constructor() {
        this.documentName = "new document"
        this.moleculs = []
    }

    reset() {
        this.documentName = "new document"
        this.moleculs = []
    }

    addMolecula(newMolecula) {
        this.moleculs.push(newMolecula)
    }

    getAtomsView() {
        var ahtml = "",
            mhtml,
            buf,
            html = "";

        this.moleculs.forEach(function(item, molIndex) {
            ahtml = ""
            item.atoms.forEach(function(id){
                buf = atomViewChunk.replace('[[id]]', id)
                buf = buf.replace('[[id]]', id)
                buf = buf.replace('[[id]]', id)
                buf = buf.replace('[[name]]', atomList[id].name)
                buf = buf.replace('[[x]]', atomList[id].x)
                buf = buf.replace('[[y]]', atomList[id].y)
                buf = buf.replace('[[z]]', atomList[id].z)
                ahtml += buf
            });
            mhtml = moleculaViewChunk.replace('[[data]]', ahtml);
            mhtml = mhtml.replace('[[title]]', item.title)
            mhtml = mhtml.replace('[[id]]', molIndex)
            html += mhtml;
        });
        console.log(html);
        return html;
    }

}
var workDocument = new WDocument();




// создание link по выбранным объектам
var sources = []
function linkCreation(ids){
    "use strict";

    console.log(ids);
    // не выбрано ниодного атома
    if (!ids) {
        sources = [];
        
        userMessage("Выберите атом #1");
        return;
    }

    //ids содержит что-то
    if (ids.length != 1) {
        console.warn("Only array with length == 1 allowed");
        return;
    }
    if (sources.length == 0){
        sources.push(ids[0]);
        userMessage("Выберите атом #2");
        return;
    } else if (sources.length == 1){
        sources.push(ids[0]);
        userMessage();
        var newLink = new WLink(sources[0], sources[1]),
            p1 = atomGroup.children[newLink.from].position,
            p2 = atomGroup.children[newLink.to].position,
            linkLine = buildLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, linkMaterial);
        addLink(newLink);
        console.log(newLink);
        console.log(atomGroup);
        selectMode('none');
    }
}

function selectFromIds(ids){
    "use strict";
    //console.log("select from ids...");

    //return default material to all atoms
    var atoms = atomGroup.children;
    for (var i = 0; i < atoms.length; i++){
        atoms[i].material = atomMaterial[i];
    }

    //change selected
    selectedAtoms = []
    for (var i = 0; i < ids.length; i++){
        selectedAtoms.push(atoms[ids[i]]);
    }

    if (controlMode == 'line'){
        linkCreation(ids);
    }

    // заполнение группы outlinesGroup
    outlinesGroup.children.splice(0);
    for (var i = 0; i < selectedAtoms.length; i++){
        var outlineMaterial = new THREE.MeshBasicMaterial({color: 0x8A00BD, side: THREE.BackSide}),
            outlineGeometry = selectedAtoms[i].geometry,
            tempMesh = selectedAtoms[i],
            outline = new THREE.Mesh(outlineGeometry, outlineMaterial);

        outline.position.set(tempMesh.position.x, tempMesh.position.y, tempMesh.position.z);
        outline.scale.multiplyScalar(1.1);
        outlinesGroup.add(outline);
    }
}


function LoadAtoms(deleteold) {
    "use strict";
    var url = "/molvi/get-last-mol-file";

    $.ajax({
        url: url,
        success: function(data){
            // $(".atomsView").html(data); !!!!!
            console.log("LoadAtoms: data loading OK");
            UpdateAtomList(data, deleteold);
        },
        error: function(data) {
            $(".atomsView").html(data.responseText);
            console.log("ERROR");
            console.log(data)
        }
    })
}

function UpdateAtomList(jsonString, deleteOld){

    //создание рабочего документа (хранит всю рабочую инфу)
    var newMolecula;
    if (deleteOld) {
        workDocument = new WDocument()
    }
    newMolecula = new WMolecula("Кластер " + (workDocument.moleculs.length + 1).toString())
    workDocument.addMolecula(newMolecula)

    atar = JSON.parse(jsonString)

    if (deleteOld === true)
        atomMaterial = [];
    //atomGroup = new THREE.Group();
    var NBefore = atomList.length
    atar.forEach(function(item, id){
        id = id + NBefore
        //var id = item['id'], // $(this).children(".id").html(),
        var x = item['x'], //$(this).children(".x").html().replace("x: ", ""),
            y = item['y'], //$(this).children(".y").html().replace("y: ", ""),
            z = item['z'], //$(this).children(".z").html().replace("z: ", ""),
            name = item['name'], //item.name$(this).children(".name").html(),
            //id = parseInt(item['id'], 10),
            x = parseFloat(item['x'], 10),
            y = parseFloat(item['y'], 10),
            z = parseFloat(item['z'], 10),
            radius = MolviConf.getAtomRadius(name),
            geometry = new THREE.SphereGeometry(radius, spehereDetalisation, spehereDetalisation),
            newMaterial = buildAtomMaterial(name),
            newMesh = new THREE.Mesh(geometry, newMaterial),
            newAtom = new WAtom(x, y, z, name);
            newMolecula.atoms.push(id);

        newMesh.position.x = x;
        newMesh.position.y = y;
        newMesh.position.z = z;
        
        atomMaterial.push(newMaterial);
        atomGroup.add(newMesh);
        atomList.push(newAtom);
    });
    buildAtomsView()
    /*while(scene.children.length > 0){ 
        scene.remove(scene.children[0]); 
    }*/
    camera.position.x = 0
    camera.position.y = 5
    camera.position.z = 0
    camera.lookAt(0,0,0);
    //buildScene();
    //scene.add(mainGroup);
    //addLight();
}

function onMouseMove(event) {
    mousePosition.x = (event.offsetX / viewWidth) * 2 - 1;
    mousePosition.y = - (event.offsetY / viewHeight) * 2 + 1;
}

function onMouseDown(event) {

    //ids = []
    var id = -1,
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
    }

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
    if (id >= 0) {
        selectFromIds([id]);
    }
}

function selectAtom(atomId) {
    "use strict";

    var selector = "#atomView_" + atomId.toString();
    $(".atomView").removeClass("selected");
    $(selector).addClass("selected");

    selectFromIds([atomId]);
}

function buildLine(x1, y1, z1, x2, y2, z2, color) {
    var array = new Float32Array([x1, y1, z1, x2, y2, z2]),
        color = new THREE.Color(color),
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

// управление режимами рисования для пользователя
function selectMode(modeName){
    "use strict";
    $(".selectedIcon").hide();
    $(".unselectedIcon").show();
    controlMode=modeName;

    if(modeName === 'line'){
        $("#icon_modeLineUnselected").hide();
        $("#icon_modeLineSelected").show();
        linkCreation();
    }
}
// авторисование связей у молекулы
function executeAutotrace(radius){
    var radius = 1.6,
        re = document.getElementById('traceRange').value;
    radius = parseFloat(re, 10);
    if (isNaN(radius)){
        console.log("Error in parse int");
        alert('Введите корректное значение длины автотрассировки');
        return;
    }



    while(linkList.length){
        deleteLink(0);
    }
    var rmin,
        numberj,
        exeptionLink=[];
    for(var i=0; i<atomList.length;i++){
        //rmin=-1;
        for(var j=0; j<atomList.length;j++){
            if(i===j){
                continue;
            }
            var r=Math.sqrt(Math.pow((atomList[i].x-atomList[j].x),2)+Math.pow(atomList[i].y-atomList[j].y,2)+Math.pow(atomList[i].z-atomList[j].z,2));
            //console.log(r);
            //if(((r<=radius && rmin<0) || r<rmin) && !exeptionLink.includes(i+j*atomList.length)){
                if(r<=radius && !exeptionLink.includes(i+j*atomList.length)){
                var newlink=new WLink(i,j);
                addLink(newlink);
                exeptionLink.push(i+atomList.length*j);
                exeptionLink.push(j+atomList.length*i);
            }
        }
        

    }
    //linkCreation();
}

function deleteLink(linkid){
    "use strict";
    linkid = parseInt(linkid);
    linkList.splice(linkid, 1);
    linkGroup.children.splice(linkid, 1);
    linkList2Html();
}

//добавить новый WLink объект
function addLink(newLink){
    "use strict";

    var p1 = atomGroup.children[newLink.from].position,
        p2 = atomGroup.children[newLink.to].position,
        linkLine = buildLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, 0xf6ff0f);
    linkGroup.add(linkLine);
    linkList.push(newLink);

    //print link list to HTML
    linkList2Html();
}

//print link list to HTML
function linkList2Html(){
    "use strict";

    var atoms = atomGroup.children,
        html = "",
        newh,
        fromIndx,
        toIndx,
        fromName,
        toName,
        fromTxt,
        toTxt;

    for (var i = 0; i < linkList.length; i++){
        fromIndx = linkList[i].from;
        toIndx = linkList[i].to;
        fromName = atomList[fromIndx].name;
        toName = atomList[toIndx].name;
        fromTxt = fromIndx.toString() + ":" + fromName;
        toTxt = toIndx.toString() + ": " + toName;
        newh = linkChunk.replace('[FROM]', fromTxt);
        newh = newh.replace('[TO]', toTxt);
        newh = newh.replace('[ID]', i).replace('[ID]', i);
        html += newh;
    }

    $(".linksView").html(html);
}


function removeLinkAt(indx){
    "use strict";
}

function autoTraceKeyPressed(e) {
    controls.enabled = false;
    if (e.keyCode == 13){
        executeAutotrace();
    }
}

function enableControls(){
    controls.enabled = true;
}
function disableControls(){
    controls.enabled = false;
}

function openFileDialog(){
    $.ajax({
        url: openFileUrl,
        success: function(data){
            console.log(data);
            var ans = data.slice(-6);
            if (ans === "<br>OK"){
                //файл успешно изменён
                buildScene();
                paintGL();
                LoadAtoms(true);
            } else {
                console.warn(data)
            }
        },
        error: function(data) {
            alert("Ошибка при открытии файла")
            console.log("open file error: " + data.toString())
        }
    })
}

function openPlusFileDialog() {
    $.ajax({
        url: openFileUrl,
        success: function(data){
            console.log(data);
            var ans = data.slice(-6);
            if (ans === "<br>OK"){
                //файл успешно изменён
                //buildScene();
                //paintGL();
                LoadAtoms(false);
            } else {
                console.warn(data)
            }
        },
        error: function(data) {
            alert("Ошибка при открытии файла")
            console.log("open file error: " + data.toString())
        }
    })
}

// вывод информации о атомах по содержанию документа
function buildAtomsView(){
    $(".atomsView").html(workDocument.getAtomsView())
}

function openMoveControls(moleculaId){
    "use strict"

    $("#moveMoleculaId").html(moleculaId)
    $('#moleculaMoveControls').show()

    $("#moveControl_x").val(0)
    $("#moveControl_y").val(0)
    $("#moveControl_z").val(0)

    controls.enabled = false
}

function closeMoveControls(){
    controls.enabled = true
    $('#moleculaMoveControls').hide()
}

function doMoleculaMove() {
    var xshift = $("#moveControl_x").val(),
        yshift = $("#moveControl_y").val(),
        zshift = $("#moveControl_z").val(),
        id = $("#moveMoleculaId").html();
    xshift = parseFloat(xshift, 10)
    yshift = parseFloat(yshift, 10)
    zshift = parseFloat(zshift, 10)
    id = parseInt(id, 10)
    if (isNaN(xshift) || isNaN(yshift) || isNaN(zshift)){
        console.log("Parse error!")
        $("#moleculaMoveControls").hide()
        return
    }
    console.log('id')
    var myArray = workDocument.moleculs[0].atoms
    myArray.forEach(function(item) {
        atomGroup.children[item].translateX(xshift)
        atomGroup.children[item].translateY(yshift)
        atomGroup.children[item].translateZ(zshift)
    })
    closeMoveControls()
}

$(document).ready(function(){
    userMessage();

    selectMode("none");
    var display = document.getElementById("display");
    display.addEventListener("mousemove", onMouseMove, false);
    display.addEventListener("mousedown", onMouseDown, false);

    initGL("display", 600, 600);
    buildScene();
    paintGL();
    LoadAtoms(true);

    var tri = document.getElementById('traceRange');
    tri.onkeypress = autoTraceKeyPressed;
    tri.value = 1.6;
    
});