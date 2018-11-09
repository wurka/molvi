/**
 * Created by teplyj-moh on 6/2/2018.
 */
let Chunks = {
    link : `
        <div class="link t1-5" id="link_0" onmouseover="engine.selectLinkById([ID])" onmouseout="engine.unselectLinks()">
            <div class="line">
                <div class='text t1-5'>
                    <span class="name">[name]</span>
                </div>
                <div class="change-length text t1-5" onclick="openChangeLinkLengthPanel([ID], [value])"><img src="/static/editor/images/change-length.svg" alt="cl.png"></div>
                <div class="change-lengthcell text t1-5" onclick="openLinkRotationPanel([ID], [FROM], [TO])"><img src="/static/editor/images/spin.svg" alt="lr.png"></div>
                <div class="deleteLink text t1-5" title="delete link" onclick="engine.deleteLink([ID])"><img src="/static/editor/images/cross-20.png" alt="cross.png"></div>
            </div>
            <div class="line">
                <div class="current-value t1-5">[value]</div>
            </div>
        </div>
    `,
    atom: `
        <div class="atomView" onclick="engine.selectAtomById([[id]])" id="atomView_[[id]]">
            <div class="name t1-5">[[name]]</div>
            <div class="id t1-5">[[id]] </div>            
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
        `,
    valenceAngle: `
        <div class="valence-angle" onclick="engine.selectAtomsById(['[atom1]', '[atom2]', '[atom3]']); engine.selectLinksById(['[link1]', '[link2]'])"  onmouseover="engine.selectAtomsById(['[atom1]', '[atom2]', '[atom3]']); engine.selectLinksById(['[link1]', '[link2]'])">
            <div class="title">[title]</div>
            <div class="buttons">
                <div class="button deleteva" onclick="deleteValenceAngle([id])" title="Удалить"><img src="/static/editor/images/cross-20.png" alt="cross.png"></div>
                <div class="button editva" onclick="editValenceAngle([id], [value])" title="Изменить угол"><img src="/static/editor/images/pen.svg" alt="pen"></div>
            </div>
            <div class="value">[value]</div>
        </div>       
    `
};