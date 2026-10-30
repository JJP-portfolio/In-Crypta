gdjs.Nivel_323Code = {};
gdjs.Nivel_323Code.localVariables = [];
gdjs.Nivel_323Code.idToCallbackMap = new Map();
gdjs.Nivel_323Code.GDJugadorObjects1_1final = [];

gdjs.Nivel_323Code.GDFondoObjects1= [];
gdjs.Nivel_323Code.GDFondoObjects2= [];
gdjs.Nivel_323Code.GDFondoObjects3= [];
gdjs.Nivel_323Code.GDSolidoObjects1= [];
gdjs.Nivel_323Code.GDSolidoObjects2= [];
gdjs.Nivel_323Code.GDSolidoObjects3= [];
gdjs.Nivel_323Code.GDJugadorObjects1= [];
gdjs.Nivel_323Code.GDJugadorObjects2= [];
gdjs.Nivel_323Code.GDJugadorObjects3= [];
gdjs.Nivel_323Code.GDEnemyObjects1= [];
gdjs.Nivel_323Code.GDEnemyObjects2= [];
gdjs.Nivel_323Code.GDEnemyObjects3= [];
gdjs.Nivel_323Code.GDAlmaObjects1= [];
gdjs.Nivel_323Code.GDAlmaObjects2= [];
gdjs.Nivel_323Code.GDAlmaObjects3= [];
gdjs.Nivel_323Code.GDPinchosObjects1= [];
gdjs.Nivel_323Code.GDPinchosObjects2= [];
gdjs.Nivel_323Code.GDPinchosObjects3= [];
gdjs.Nivel_323Code.GDPuertaObjects1= [];
gdjs.Nivel_323Code.GDPuertaObjects2= [];
gdjs.Nivel_323Code.GDPuertaObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595BarraObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595BarraObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595BarraObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595NivelObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595NivelObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595NivelObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595VidasObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595VidasObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595VidasObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595DashObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595DashObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595DashObjects3= [];
gdjs.Nivel_323Code.GDHUD_9595PistaObjects1= [];
gdjs.Nivel_323Code.GDHUD_9595PistaObjects2= [];
gdjs.Nivel_323Code.GDHUD_9595PistaObjects3= [];
gdjs.Nivel_323Code.GDPalaRecogibleObjects1= [];
gdjs.Nivel_323Code.GDPalaRecogibleObjects2= [];
gdjs.Nivel_323Code.GDPalaRecogibleObjects3= [];
gdjs.Nivel_323Code.GDPlataformaMovilObjects1= [];
gdjs.Nivel_323Code.GDPlataformaMovilObjects2= [];
gdjs.Nivel_323Code.GDPlataformaMovilObjects3= [];
gdjs.Nivel_323Code.GDGolpePalaObjects1= [];
gdjs.Nivel_323Code.GDGolpePalaObjects2= [];
gdjs.Nivel_323Code.GDGolpePalaObjects3= [];


gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects2Objects = Hashtable.newFrom({"GolpePala": gdjs.Nivel_323Code.GDGolpePalaObjects2});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects1Objects = Hashtable.newFrom({"GolpePala": gdjs.Nivel_323Code.GDGolpePalaObjects1});
gdjs.Nivel_323Code.eventsList0 = function(runtimeScene) {

{

gdjs.copyArray(gdjs.Nivel_323Code.GDJugadorObjects1, gdjs.Nivel_323Code.GDJugadorObjects2);


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects2[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects2[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects2[k] = gdjs.Nivel_323Code.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects2.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects2 */
gdjs.Nivel_323Code.GDGolpePalaObjects2.length = 0;

{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects2[i].setAnimation(2);
}
}
{gdjs.evtTools.object.createObjectOnScene(runtimeScene, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects2Objects, (( gdjs.Nivel_323Code.GDJugadorObjects2.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects2[0].getPointX("")) + 24, (( gdjs.Nivel_323Code.GDJugadorObjects2.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects2[0].getPointY("")) + 2, "");
}
}

}


{

/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
gdjs.Nivel_323Code.GDGolpePalaObjects1.length = 0;

{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(5);
}
}
{gdjs.evtTools.object.createObjectOnScene(runtimeScene, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects1Objects, (( gdjs.Nivel_323Code.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects1[0].getPointX("")) - 24, (( gdjs.Nivel_323Code.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects1[0].getPointY("")) + 2, "");
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].setAnimation(3);
}
}
}

}


};gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects1Objects = Hashtable.newFrom({"GolpePala": gdjs.Nivel_323Code.GDGolpePalaObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects = Hashtable.newFrom({"Enemy": gdjs.Nivel_323Code.GDEnemyObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDAlmaObjects1Objects = Hashtable.newFrom({"Alma": gdjs.Nivel_323Code.GDAlmaObjects1});
gdjs.Nivel_323Code.eventsList1 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() < 5);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).add(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Vida", false, 100, 1);
}
}

}


};gdjs.Nivel_323Code.eventsList2 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(3).getAsNumber() >= 10);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}

{ //Subevents
gdjs.Nivel_323Code.eventsList1(runtimeScene);} //End of subevents
}

}


};gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPalaRecogibleObjects1Objects = Hashtable.newFrom({"PalaRecogible": gdjs.Nivel_323Code.GDPalaRecogibleObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects = Hashtable.newFrom({"Enemy": gdjs.Nivel_323Code.GDEnemyObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects = Hashtable.newFrom({"Enemy": gdjs.Nivel_323Code.GDEnemyObjects1});
gdjs.Nivel_323Code.eventsList3 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, gdjs.evtTools.runtimeScene.getSceneName(runtimeScene), false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() <= 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", false);
}
}

}


};gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPinchosObjects1Objects = Hashtable.newFrom({"Pinchos": gdjs.Nivel_323Code.GDPinchosObjects1});
gdjs.Nivel_323Code.eventsList4 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, gdjs.evtTools.runtimeScene.getSceneName(runtimeScene), false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() <= 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", false);
}
}

}


};gdjs.Nivel_323Code.eventsList5 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, gdjs.evtTools.runtimeScene.getSceneName(runtimeScene), false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() <= 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", false);
}
}

}


};gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.Nivel_323Code.GDJugadorObjects1});
gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPuertaObjects1Objects = Hashtable.newFrom({"Puerta": gdjs.Nivel_323Code.GDPuertaObjects1});
gdjs.Nivel_323Code.eventsList6 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(4)) == 1;
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, gdjs.evtTools.runtimeScene.getSceneName(runtimeScene), false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)).setNumber(1);
}
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 2, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 480, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 270, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 2, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 480, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 270, "UI", 0);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Escape");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.pushScene(runtimeScene, "Pausa");
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Left");
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)).setNumber(-1);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateLeftKey();
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Right");
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateRightKey();
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(7)).setNumber(0.12);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(6)).setNumber(0.10);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(6)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(7)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(7)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(7)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{gdjs.Nivel_323Code.GDJugadorObjects1_1final.length = 0;
let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
gdjs.copyArray(gdjs.Nivel_323Code.GDJugadorObjects1, gdjs.Nivel_323Code.GDJugadorObjects2);

for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects2[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_1 = true;
        gdjs.Nivel_323Code.GDJugadorObjects2[k] = gdjs.Nivel_323Code.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects2.length = k;
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
    for (let j = 0, jLen = gdjs.Nivel_323Code.GDJugadorObjects2.length; j < jLen ; ++j) {
        if ( gdjs.Nivel_323Code.GDJugadorObjects1_1final.indexOf(gdjs.Nivel_323Code.GDJugadorObjects2[j]) === -1 )
            gdjs.Nivel_323Code.GDJugadorObjects1_1final.push(gdjs.Nivel_323Code.GDJugadorObjects2[j]);
    }
}
}
{
gdjs.copyArray(gdjs.Nivel_323Code.GDJugadorObjects1, gdjs.Nivel_323Code.GDJugadorObjects2);

for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects2[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects2[i].getVariables().getFromIndex(6)) > 0 ) {
        isConditionTrue_1 = true;
        gdjs.Nivel_323Code.GDJugadorObjects2[k] = gdjs.Nivel_323Code.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects2.length = k;
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
    for (let j = 0, jLen = gdjs.Nivel_323Code.GDJugadorObjects2.length; j < jLen ; ++j) {
        if ( gdjs.Nivel_323Code.GDJugadorObjects1_1final.indexOf(gdjs.Nivel_323Code.GDJugadorObjects2[j]) === -1 )
            gdjs.Nivel_323Code.GDJugadorObjects1_1final.push(gdjs.Nivel_323Code.GDJugadorObjects2[j]);
    }
}
}
{
gdjs.copyArray(gdjs.Nivel_323Code.GDJugadorObjects1_1final, gdjs.Nivel_323Code.GDJugadorObjects1);
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateJumpKey();
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Salto", false, 100, 1);
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(7)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(6)).setNumber(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Up");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateJumpKey();
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "a");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Pala", false, 100, 1);
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)).setNumber(0.18);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(10)).setNumber(0.40);
}
}

{ //Subevents
gdjs.Nivel_323Code.eventsList0(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) <= 0.12 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) > 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].setAnimation(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) <= 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].setAnimation(2);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) <= 0.12 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) > 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].setAnimation(4);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) <= 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].setAnimation(5);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(9)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)).setNumber(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(10)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(10)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDGolpePalaObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDEnemyObjects1 */
/* Reuse gdjs.Nivel_323Code.GDGolpePalaObjects1 */
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDEnemyObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDEnemyObjects1[i].deleteFromScene(runtimeScene);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].deleteFromScene(runtimeScene);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDGolpePalaObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDGolpePalaObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDGolpePalaObjects1[k] = gdjs.Nivel_323Code.GDGolpePalaObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDGolpePalaObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDGolpePalaObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].returnVariable(gdjs.Nivel_323Code.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.Nivel_323Code.GDGolpePalaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDGolpePalaObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDGolpePalaObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDGolpePalaObjects1[k] = gdjs.Nivel_323Code.GDGolpePalaObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDGolpePalaObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDGolpePalaObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDGolpePalaObjects1[i].deleteFromScene(runtimeScene);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(6);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(3);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(8);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(7);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(4);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(8)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setAnimation(9);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "LShift");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "RShift");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dash", false, 100, 1);
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(0.16);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0.60);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(560.0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(0, true);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560.0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "LShift");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "RShift");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dash", false, 100, 1);
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(0.16);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0.60);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(560.0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(0, true);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560.0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(3)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560.0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentFallSpeed(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(3)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(3)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(2)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(1500);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(250);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(900, true);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed(0);
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(1);
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].setX(Math.min(Math.max((gdjs.Nivel_323Code.GDJugadorObjects1[i].getPointX("")), 0), 5856));
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("PlataformaMovil"), gdjs.Nivel_323Code.GDPlataformaMovilObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDPlataformaMovilObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].setX((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(0))) + Math.sin(gdjs.evtTools.runtimeScene.getTimeFromStartInSeconds(runtimeScene) * (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(3))) + (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(4)))) * (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(2))) * (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(5))));
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDPlataformaMovilObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].setY((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(1))) + Math.sin(gdjs.evtTools.runtimeScene.getTimeFromStartInSeconds(runtimeScene) * (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(3))) + (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(4)))) * (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(2))) * (1 - (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDPlataformaMovilObjects1[i].getVariables().getFromIndex(5)))));
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
{gdjs.evtTools.camera.setCameraX(runtimeScene, Math.min(Math.max((( gdjs.Nivel_323Code.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects1[0].getPointX("")) + 16, 480), 5408), "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, Math.min(Math.max((( gdjs.Nivel_323Code.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDJugadorObjects1[0].getPointY("")) + 16, 270), 306), "", 0);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDEnemyObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDEnemyObjects1[k] = gdjs.Nivel_323Code.GDEnemyObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDEnemyObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDEnemyObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDEnemyObjects1[i].getX() >= (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(2))) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDEnemyObjects1[k] = gdjs.Nivel_323Code.GDEnemyObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDEnemyObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDEnemyObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDEnemyObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDEnemyObjects1[i].returnVariable(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(0)).setNumber(-1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDEnemyObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDEnemyObjects1[k] = gdjs.Nivel_323Code.GDEnemyObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDEnemyObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDEnemyObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDEnemyObjects1[i].getX() <= (gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(1))) ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDEnemyObjects1[k] = gdjs.Nivel_323Code.GDEnemyObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDEnemyObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDEnemyObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDEnemyObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDEnemyObjects1[i].returnVariable(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(0)).setNumber(1);
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDEnemyObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDEnemyObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.Nivel_323Code.GDEnemyObjects1[i].getVariables().getFromIndex(0))) * 55);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Alma"), gdjs.Nivel_323Code.GDAlmaObjects1);
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDAlmaObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDAlmaObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDAlmaObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDAlmaObjects1[i].deleteFromScene(runtimeScene);
}
}
{runtimeScene.getGame().getVariables().getFromIndex(1).add(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).add(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma", false, 100, 1);
}

{ //Subevents
gdjs.Nivel_323Code.eventsList2(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("PalaRecogible"), gdjs.Nivel_323Code.GDPalaRecogibleObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPalaRecogibleObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
/* Reuse gdjs.Nivel_323Code.GDPalaRecogibleObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDPalaRecogibleObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDPalaRecogibleObjects1[i].deleteFromScene(runtimeScene);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_PalaRecoger", false, 100, 1);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getY() < (( gdjs.Nivel_323Code.GDEnemyObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDEnemyObjects1[0].getPointY("")) - 10 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.Nivel_323Code.GDEnemyObjects1 */
/* Reuse gdjs.Nivel_323Code.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.Nivel_323Code.GDEnemyObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDEnemyObjects1[i].deleteFromScene(runtimeScene);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDJugadorObjects1[i].returnVariable(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Golpe", false, 100, 1);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Enemy"), gdjs.Nivel_323Code.GDEnemyObjects1);
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDEnemyObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getY() >= (( gdjs.Nivel_323Code.GDEnemyObjects1.length === 0 ) ? 0 :gdjs.Nivel_323Code.GDEnemyObjects1[0].getPointY("")) - 10 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).sub(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dano", false, 100, 1);
}

{ //Subevents
gdjs.Nivel_323Code.eventsList3(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("Pinchos"), gdjs.Nivel_323Code.GDPinchosObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPinchosObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).sub(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dano", false, 100, 1);
}

{ //Subevents
gdjs.Nivel_323Code.eventsList4(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getY() > 696 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).sub(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dano", false, 100, 1);
}

{ //Subevents
gdjs.Nivel_323Code.eventsList5(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("Puerta"), gdjs.Nivel_323Code.GDPuertaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDJugadorObjects1Objects, gdjs.Nivel_323Code.mapOfGDgdjs_9546Nivel_9595323Code_9546GDPuertaObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Meta", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).add(runtimeScene.getGame().getVariables().getFromIndex(1).getAsNumber());
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Victoria", false);
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("HUD_Almas"), gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1);
gdjs.copyArray(runtimeScene.getObjects("HUD_Vidas"), gdjs.Nivel_323Code.GDHUD_9595VidasObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1[i].setString("ALMAS " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(1))) + " · VIDA +" + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(3))) + "/10");
}
}
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595VidasObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595VidasObjects1[i].setString("VIDAS " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(0))) + "/5");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() <= 1);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Aviso"), gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1[i].setString("¡ÚLTIMA VIDA!");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 1);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Aviso"), gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1[i].setString("");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Dash"), gdjs.Nivel_323Code.GDHUD_9595DashObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595DashObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595DashObjects1[i].setString("SHIFT: DASH · A: PALA");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.Nivel_323Code.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.Nivel_323Code.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariableNumber(gdjs.Nivel_323Code.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.Nivel_323Code.GDJugadorObjects1[k] = gdjs.Nivel_323Code.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.Nivel_323Code.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Dash"), gdjs.Nivel_323Code.GDHUD_9595DashObjects1);
{for(var i = 0, len = gdjs.Nivel_323Code.GDHUD_9595DashObjects1.length ;i < len;++i) {
    gdjs.Nivel_323Code.GDHUD_9595DashObjects1[i].setString("SHIFT: DASH");
}
}
}

}


};

gdjs.Nivel_323Code.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.Nivel_323Code.GDFondoObjects1.length = 0;
gdjs.Nivel_323Code.GDFondoObjects2.length = 0;
gdjs.Nivel_323Code.GDFondoObjects3.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects1.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects2.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects3.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects1.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects2.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects3.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects1.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects2.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects3.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects1.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects2.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects3.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects1.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects2.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects3.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects1.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects2.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects3.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects1.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects2.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects3.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects1.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects2.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects3.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects1.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects2.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects3.length = 0;

gdjs.Nivel_323Code.eventsList6(runtimeScene);
gdjs.Nivel_323Code.GDFondoObjects1.length = 0;
gdjs.Nivel_323Code.GDFondoObjects2.length = 0;
gdjs.Nivel_323Code.GDFondoObjects3.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects1.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects2.length = 0;
gdjs.Nivel_323Code.GDSolidoObjects3.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects1.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects2.length = 0;
gdjs.Nivel_323Code.GDJugadorObjects3.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects1.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects2.length = 0;
gdjs.Nivel_323Code.GDEnemyObjects3.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects1.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects2.length = 0;
gdjs.Nivel_323Code.GDAlmaObjects3.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects1.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects2.length = 0;
gdjs.Nivel_323Code.GDPinchosObjects3.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects1.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects2.length = 0;
gdjs.Nivel_323Code.GDPuertaObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595BarraInferiorObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595NivelObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AlmasObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595VidasObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595AvisoObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595DashObjects3.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects1.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects2.length = 0;
gdjs.Nivel_323Code.GDHUD_9595PistaObjects3.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects1.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects2.length = 0;
gdjs.Nivel_323Code.GDPalaRecogibleObjects3.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects1.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects2.length = 0;
gdjs.Nivel_323Code.GDPlataformaMovilObjects3.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects1.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects2.length = 0;
gdjs.Nivel_323Code.GDGolpePalaObjects3.length = 0;


return;

}

gdjs['Nivel_323Code'] = gdjs.Nivel_323Code;
