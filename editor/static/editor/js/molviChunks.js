/**
 * Created by teplyj-moh on 6/2/2018.
 */
var Chunks = {
    link : `
        <div class="link" id="link_0" onmouseover="engine.selectLinkById([ID])" onmouseout="engine.unselectLinks()">
            <div class='cell'>
                <span>[FROM]</span><span> - </span><span>[TO]</span>
            </div>
            <div class="change-length cell" onclick="openChangeLinkLengthPanel([ID], [length])"><img src="/static/editor/images/change-length.png" alt="cl.png"></div>
            <div class="change-length cell" onclick="openLinkRotationPanel([ID], [FROM], [TO])"><img src="/static/editor/images/link-rotation-20.png" alt="lr.png"></div>
            <div class="deleteLink cell" title="delete link" onclick="engine.deleteLink([ID])">x</div>
        </div>
    `,
    atom: `
        <div class="atomView" onclick="engine.selectAtomById([[id]])" id="atomView_[[id]]">
            <div class="id">[[id]]: </div>
            <div class="name">[[name]]</div>
            <div class="devider"></div>
            <div class="x" contenteditable>x: [[x]]</div>
            <div class="y" contenteditable>y: [[y]]</div>
            <div class="z" contenteditable>z: [[z]]</div>
        </div>
    `,
    cluster: `
        <div class="clusterView">
            <div class="title">
                <span>[[title]] </span><div style="text-decoration: underline" class='move' onclick='engine.openMoveControls([[id]])'>переместить</div>
            </div>
            <div class="moleculaData">
                [[data]]
            </div>
        </div>
        `
};