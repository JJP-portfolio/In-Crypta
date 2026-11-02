gdjs.TutorialCode = {};
gdjs.TutorialCode.localVariables = [];
gdjs.TutorialCode.idToCallbackMap = new Map();
gdjs.TutorialCode.GDJugadorObjects1_1final = [];

gdjs.TutorialCode.GDFondoObjects1= [];
gdjs.TutorialCode.GDFondoObjects2= [];
gdjs.TutorialCode.GDFondoObjects3= [];
gdjs.TutorialCode.GDSolidoObjects1= [];
gdjs.TutorialCode.GDSolidoObjects2= [];
gdjs.TutorialCode.GDSolidoObjects3= [];
gdjs.TutorialCode.GDJugadorObjects1= [];
gdjs.TutorialCode.GDJugadorObjects2= [];
gdjs.TutorialCode.GDJugadorObjects3= [];
gdjs.TutorialCode.GDPuertaObjects1= [];
gdjs.TutorialCode.GDPuertaObjects2= [];
gdjs.TutorialCode.GDPuertaObjects3= [];
gdjs.TutorialCode.GDHUD_9595BarraObjects1= [];
gdjs.TutorialCode.GDHUD_9595BarraObjects2= [];
gdjs.TutorialCode.GDHUD_9595BarraObjects3= [];
gdjs.TutorialCode.GDHUD_9595NivelObjects1= [];
gdjs.TutorialCode.GDHUD_9595NivelObjects2= [];
gdjs.TutorialCode.GDHUD_9595NivelObjects3= [];
gdjs.TutorialCode.GDHUD_9595AlmasObjects1= [];
gdjs.TutorialCode.GDHUD_9595AlmasObjects2= [];
gdjs.TutorialCode.GDHUD_9595AlmasObjects3= [];
gdjs.TutorialCode.GDHUD_9595VidasObjects1= [];
gdjs.TutorialCode.GDHUD_9595VidasObjects2= [];
gdjs.TutorialCode.GDHUD_9595VidasObjects3= [];
gdjs.TutorialCode.GDHUD_9595AvisoObjects1= [];
gdjs.TutorialCode.GDHUD_9595AvisoObjects2= [];
gdjs.TutorialCode.GDHUD_9595AvisoObjects3= [];
gdjs.TutorialCode.GDHUD_9595ControlesObjects1= [];
gdjs.TutorialCode.GDHUD_9595ControlesObjects2= [];
gdjs.TutorialCode.GDHUD_9595ControlesObjects3= [];
gdjs.TutorialCode.GDJefeObjects1= [];
gdjs.TutorialCode.GDJefeObjects2= [];
gdjs.TutorialCode.GDJefeObjects3= [];
gdjs.TutorialCode.GDOndaIzqObjects1= [];
gdjs.TutorialCode.GDOndaIzqObjects2= [];
gdjs.TutorialCode.GDOndaIzqObjects3= [];
gdjs.TutorialCode.GDOndaDerObjects1= [];
gdjs.TutorialCode.GDOndaDerObjects2= [];
gdjs.TutorialCode.GDOndaDerObjects3= [];
gdjs.TutorialCode.GDGolpePalaObjects1= [];
gdjs.TutorialCode.GDGolpePalaObjects2= [];
gdjs.TutorialCode.GDGolpePalaObjects3= [];
gdjs.TutorialCode.GDAlmaObjects1= [];
gdjs.TutorialCode.GDAlmaObjects2= [];
gdjs.TutorialCode.GDAlmaObjects3= [];
gdjs.TutorialCode.GDFarolCheckpointObjects1= [];
gdjs.TutorialCode.GDFarolCheckpointObjects2= [];
gdjs.TutorialCode.GDFarolCheckpointObjects3= [];
gdjs.TutorialCode.GDPalaRecogibleObjects1= [];
gdjs.TutorialCode.GDPalaRecogibleObjects2= [];
gdjs.TutorialCode.GDPalaRecogibleObjects3= [];
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects1= [];
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects2= [];
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects3= [];
gdjs.TutorialCode.GDHUD_9595IconoDashObjects1= [];
gdjs.TutorialCode.GDHUD_9595IconoDashObjects2= [];
gdjs.TutorialCode.GDHUD_9595IconoDashObjects3= [];
gdjs.TutorialCode.GDHUD_9595CorazonObjects1= [];
gdjs.TutorialCode.GDHUD_9595CorazonObjects2= [];
gdjs.TutorialCode.GDHUD_9595CorazonObjects3= [];


gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDGolpePalaObjects2Objects = Hashtable.newFrom({"GolpePala": gdjs.TutorialCode.GDGolpePalaObjects2});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDGolpePalaObjects1Objects = Hashtable.newFrom({"GolpePala": gdjs.TutorialCode.GDGolpePalaObjects1});
gdjs.TutorialCode.eventsList0 = function(runtimeScene) {

{

gdjs.copyArray(gdjs.TutorialCode.GDJugadorObjects1, gdjs.TutorialCode.GDJugadorObjects2);


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects2[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects2[k] = gdjs.TutorialCode.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects2.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects2 */
gdjs.TutorialCode.GDGolpePalaObjects2.length = 0;

{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].setAnimation(2);
}
}
{gdjs.evtTools.object.createObjectOnScene(runtimeScene, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDGolpePalaObjects2Objects, (( gdjs.TutorialCode.GDJugadorObjects2.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects2[0].getPointX("")) + 24, (( gdjs.TutorialCode.GDJugadorObjects2.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects2[0].getPointY("")) + 2, "");
}
}

}


{

/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
gdjs.TutorialCode.GDGolpePalaObjects1.length = 0;

{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(5);
}
}
{gdjs.evtTools.object.createObjectOnScene(runtimeScene, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDGolpePalaObjects1Objects, (( gdjs.TutorialCode.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects1[0].getPointX("")) - 24, (( gdjs.TutorialCode.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects1[0].getPointY("")) + 2, "");
}
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].setAnimation(3);
}
}
}

}


};gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.TutorialCode.GDJugadorObjects1});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDAlmaObjects1Objects = Hashtable.newFrom({"Alma": gdjs.TutorialCode.GDAlmaObjects1});
gdjs.TutorialCode.eventsList1 = function(runtimeScene) {

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


};gdjs.TutorialCode.eventsList2 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() > 6);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(6);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 1);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma1", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 2);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma2", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 3);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma3", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 4);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma4", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 5);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma5", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(4).getAsNumber() == 6);
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma6", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(3).getAsNumber() >= 10);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}

{ //Subevents
gdjs.TutorialCode.eventsList1(runtimeScene);} //End of subevents
}

}


};gdjs.TutorialCode.eventsList3 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(5).getAsNumber() <= 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
}

}


};gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.TutorialCode.GDJugadorObjects1});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDPalaRecogibleObjects1Objects = Hashtable.newFrom({"PalaRecogible": gdjs.TutorialCode.GDPalaRecogibleObjects1});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.TutorialCode.GDJugadorObjects1});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDFarolCheckpointObjects1Objects = Hashtable.newFrom({"FarolCheckpoint": gdjs.TutorialCode.GDFarolCheckpointObjects1});
gdjs.TutorialCode.eventsList4 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(0)) < 3;
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).add(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(1)) >= gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(21)) + 5;
if (isConditionTrue_0) {
gdjs.copyArray(gdjs.TutorialCode.GDHUD_9595AvisoObjects1, gdjs.TutorialCode.GDHUD_9595AvisoObjects2);

{runtimeScene.getGame().getVariables().getFromIndex(20).setNumber(1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595AvisoObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595AvisoObjects2[i].setString("¡MANTO DEL FAROL OBTENIDO (+ESCUDO)!");
}
}
{gdjs.evtTools.runtimeScene.resetTimer(runtimeScene, "HUDNotice");
}
}

}


{


let isConditionTrue_0 = false;
{
{runtimeScene.getGame().getVariables().getFromIndex(21).setNumber(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(1)));
}
}

}


};gdjs.TutorialCode.eventsList5 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(18).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Aviso"), gdjs.TutorialCode.GDHUD_9595AvisoObjects2);
gdjs.copyArray(gdjs.TutorialCode.GDJugadorObjects1, gdjs.TutorialCode.GDJugadorObjects2);

{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].setX(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(16)));
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].setY(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(17)));
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].getBehavior("PlatformerObject").setCurrentSpeed(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].getBehavior("PlatformerObject").setCurrentFallSpeed(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(3)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(4)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(6)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects2[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(5)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595AvisoObjects2.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595AvisoObjects2[i].setString("¡REGRESO AL FAROL DE REPOSO!");
}
}
{gdjs.evtTools.runtimeScene.resetTimer(runtimeScene, "HUDNotice");
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(18).getAsNumber() == 0);
}
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(15).setNumber(0);
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
{runtimeScene.getGame().getVariables().getFromIndex(6).add(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(15).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(18).setNumber(0);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Muerte", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Derrota", false);
}
}

}


};gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects = Hashtable.newFrom({"Jugador": gdjs.TutorialCode.GDJugadorObjects1});
gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDPuertaObjects1Objects = Hashtable.newFrom({"Puerta": gdjs.TutorialCode.GDPuertaObjects1});
gdjs.TutorialCode.eventsList6 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(9)) == 1;
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(9).setNumber(0);
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
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("Solido"), gdjs.TutorialCode.GDSolidoObjects1);
{runtimeScene.getGame().getVariables().getFromIndex(8).setNumber(0);
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)).setNumber(0);
}
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(15).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(11).setNumber(512);
}
{runtimeScene.getGame().getVariables().getFromIndex(12).setNumber(224);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1.25, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 512, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 224, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 640, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 360, "UI", 0);
}
{for(var i = 0, len = gdjs.TutorialCode.GDSolidoObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDSolidoObjects1[i].hide();
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(18).getAsNumber() == 1);
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(19).getAsString() == gdjs.evtTools.runtimeScene.getSceneName(runtimeScene));
}
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setX(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(16)));
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setY(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(17)));
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "F1");
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(7).setNumber(1 - gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(7)));
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Escape");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.pushScene(runtimeScene, "Pausa");
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Left");
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)).setNumber(-1);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateLeftKey();
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Right");
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateRightKey();
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)).setNumber(0.12);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(7)).setNumber(0.10);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(6)).setNumber(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(7)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(7)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(1500);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(295);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setJumpSpeed(620);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCanJump();
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateJumpKey();
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 295);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(7)).setNumber(0);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Salto", false, 100, 1);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{gdjs.TutorialCode.GDJugadorObjects1_1final.length = 0;
let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
gdjs.copyArray(gdjs.TutorialCode.GDJugadorObjects1, gdjs.TutorialCode.GDJugadorObjects2);

for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects2[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_1 = true;
        gdjs.TutorialCode.GDJugadorObjects2[k] = gdjs.TutorialCode.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects2.length = k;
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
    for (let j = 0, jLen = gdjs.TutorialCode.GDJugadorObjects2.length; j < jLen ; ++j) {
        if ( gdjs.TutorialCode.GDJugadorObjects1_1final.indexOf(gdjs.TutorialCode.GDJugadorObjects2[j]) === -1 )
            gdjs.TutorialCode.GDJugadorObjects1_1final.push(gdjs.TutorialCode.GDJugadorObjects2[j]);
    }
}
}
{
gdjs.copyArray(gdjs.TutorialCode.GDJugadorObjects1, gdjs.TutorialCode.GDJugadorObjects2);

for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects2.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects2[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects2[i].getVariables().getFromIndex(7)) > 0 ) {
        isConditionTrue_1 = true;
        gdjs.TutorialCode.GDJugadorObjects2[k] = gdjs.TutorialCode.GDJugadorObjects2[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects2.length = k;
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
    for (let j = 0, jLen = gdjs.TutorialCode.GDJugadorObjects2.length; j < jLen ; ++j) {
        if ( gdjs.TutorialCode.GDJugadorObjects1_1final.indexOf(gdjs.TutorialCode.GDJugadorObjects2[j]) === -1 )
            gdjs.TutorialCode.GDJugadorObjects1_1final.push(gdjs.TutorialCode.GDJugadorObjects2[j]);
    }
}
}
{
gdjs.copyArray(gdjs.TutorialCode.GDJugadorObjects1_1final, gdjs.TutorialCode.GDJugadorObjects1);
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setJumpSpeed(620);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCanJump();
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateJumpKey();
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Salto", false, 100, 1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(8)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(7)).setNumber(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isKeyPressed(runtimeScene, "Space");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").simulateJumpKey();
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "x");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "X");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dash", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(3.5);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0.1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0.20);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(0.60);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(6)).setNumber(1);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(560);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(0, false);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "x");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "X");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(6)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dash", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(3.5);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0.1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)).setNumber(0.20);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)).setNumber(0.60);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(6)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(560);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(0, false);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 560);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentFallSpeed(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(4)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)).setNumber(0);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setGravity(1500);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxSpeed(250);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setMaxFallingSpeed(900, false);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").setCurrentSpeed((gdjs.RuntimeObject.getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0))) * 250);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "j");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "J");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.isMouseButtonPressed(runtimeScene, "\"Left\"");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(11)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Pala", false, 100, 1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)).setNumber(0.18);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(11)).setNumber(0.40);
}
}

{ //Subevents
gdjs.TutorialCode.eventsList0(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0.12 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) > 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].setAnimation(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].setAnimation(2);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0.12 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) > 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].setAnimation(4);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0.06 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].setAnimation(5);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(10)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)).setNumber(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(11)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(11)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDGolpePalaObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDGolpePalaObjects1[i].getVariableNumber(gdjs.TutorialCode.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDGolpePalaObjects1[k] = gdjs.TutorialCode.GDGolpePalaObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDGolpePalaObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDGolpePalaObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].returnVariable(gdjs.TutorialCode.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("GolpePala"), gdjs.TutorialCode.GDGolpePalaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDGolpePalaObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDGolpePalaObjects1[i].getVariableNumber(gdjs.TutorialCode.GDGolpePalaObjects1[i].getVariables().getFromIndex(0)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDGolpePalaObjects1[k] = gdjs.TutorialCode.GDGolpePalaObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDGolpePalaObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDGolpePalaObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDGolpePalaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDGolpePalaObjects1[i].deleteFromScene(runtimeScene);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(14);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(15);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(2);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(5);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(12);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(13);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(7);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(4);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isJumping()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(9);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(10);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(11);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(6);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(3);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(9)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isOnFloor() ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( !(gdjs.TutorialCode.GDJugadorObjects1[i].getBehavior("PlatformerObject").isMovingEvenALittle()) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(0)) == -1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].setAnimation(8);
}
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
{runtimeScene.getGame().getVariables().getFromIndex(14).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}
{runtimeScene.getGame().getVariables().getFromIndex(11).setNumber(runtimeScene.getGame().getVariables().getFromIndex(11).getAsNumber() + (Math.min(Math.max((( gdjs.TutorialCode.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects1[0].getPointX("")) + 16, 512), 2048) - runtimeScene.getGame().getVariables().getFromIndex(11).getAsNumber()) * Math.min(1, 7.0 * gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene)));
}
{runtimeScene.getGame().getVariables().getFromIndex(12).setNumber(runtimeScene.getGame().getVariables().getFromIndex(12).getAsNumber() + (Math.min(Math.max((( gdjs.TutorialCode.GDJugadorObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDJugadorObjects1[0].getPointY("")) + 16, 224), 224) - runtimeScene.getGame().getVariables().getFromIndex(12).getAsNumber()) * Math.min(1, 7.0 * gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene)));
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, runtimeScene.getGame().getVariables().getFromIndex(11).getAsNumber() + gdjs.randomInRange(-(((1 - gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(7))) * (runtimeScene.getGame().getVariables().getFromIndex(13).getAsNumber() * Math.max(0, runtimeScene.getGame().getVariables().getFromIndex(14).getAsNumber()) / 0.18))), ((1 - gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(7))) * (runtimeScene.getGame().getVariables().getFromIndex(13).getAsNumber() * Math.max(0, runtimeScene.getGame().getVariables().getFromIndex(14).getAsNumber()) / 0.18))), "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, runtimeScene.getGame().getVariables().getFromIndex(12).getAsNumber() + gdjs.randomInRange(-(((1 - gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(7))) * (runtimeScene.getGame().getVariables().getFromIndex(13).getAsNumber() * Math.max(0, runtimeScene.getGame().getVariables().getFromIndex(14).getAsNumber()) / 0.18))), ((1 - gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(7))) * (runtimeScene.getGame().getVariables().getFromIndex(13).getAsNumber() * Math.max(0, runtimeScene.getGame().getVariables().getFromIndex(14).getAsNumber()) / 0.18))), "", 0);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Alma"), gdjs.TutorialCode.GDAlmaObjects1);
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDAlmaObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDAlmaObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDAlmaObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDAlmaObjects1[i].deleteFromScene(runtimeScene);
}
}
{runtimeScene.getGame().getVariables().getFromIndex(1).add(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).add(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).add(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(1.3);
}

{ //Subevents
gdjs.TutorialCode.eventsList2(runtimeScene);} //End of subevents
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(5).getAsNumber() > 0);
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(5).sub(gdjs.evtTools.runtimeScene.getElapsedTimeInSeconds(runtimeScene));
}

{ //Subevents
gdjs.TutorialCode.eventsList3(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("PalaRecogible"), gdjs.TutorialCode.GDPalaRecogibleObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDPalaRecogibleObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDJugadorObjects1 */
/* Reuse gdjs.TutorialCode.GDPalaRecogibleObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDPalaRecogibleObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDPalaRecogibleObjects1[i].deleteFromScene(runtimeScene);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDJugadorObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDJugadorObjects1[i].returnVariable(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)).setNumber(1);
}
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_PalaRecoger", false, 100, 1);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("FarolCheckpoint"), gdjs.TutorialCode.GDFarolCheckpointObjects1);
gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDFarolCheckpointObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDFarolCheckpointObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDFarolCheckpointObjects1[i].getVariableNumber(gdjs.TutorialCode.GDFarolCheckpointObjects1[i].getVariables().get("activo")) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDFarolCheckpointObjects1[k] = gdjs.TutorialCode.GDFarolCheckpointObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDFarolCheckpointObjects1.length = k;
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDFarolCheckpointObjects1 */
gdjs.copyArray(runtimeScene.getObjects("HUD_Aviso"), gdjs.TutorialCode.GDHUD_9595AvisoObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDFarolCheckpointObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDFarolCheckpointObjects1[i].returnVariable(gdjs.TutorialCode.GDFarolCheckpointObjects1[i].getVariables().get("activo")).setNumber(1);
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDFarolCheckpointObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDFarolCheckpointObjects1[i].setAnimation(1);
}
}
{runtimeScene.getGame().getVariables().getFromIndex(18).setNumber(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(16).setNumber((( gdjs.TutorialCode.GDFarolCheckpointObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDFarolCheckpointObjects1[0].getPointX("")));
}
{runtimeScene.getGame().getVariables().getFromIndex(17).setNumber((( gdjs.TutorialCode.GDFarolCheckpointObjects1.length === 0 ) ? 0 :gdjs.TutorialCode.GDFarolCheckpointObjects1[0].getPointY("")));
}
{runtimeScene.getGame().getVariables().getFromIndex(19).setString(gdjs.evtTools.runtimeScene.getSceneName(runtimeScene));
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Alma", false, 100, 1);
}
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595AvisoObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595AvisoObjects1[i].setString("¡PUNTO DE CONTROL ALCANZADO!");
}
}
{gdjs.evtTools.runtimeScene.resetTimer(runtimeScene, "HUDNotice");
}

{ //Subevents
gdjs.TutorialCode.eventsList4(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getY() > 568 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).sub(1);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Dano", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(9.0);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0.22);
}

{ //Subevents
gdjs.TutorialCode.eventsList5(runtimeScene);} //End of subevents
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);
gdjs.copyArray(runtimeScene.getObjects("Puerta"), gdjs.TutorialCode.GDPuertaObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.object.hitBoxesCollisionTest(gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDJugadorObjects1Objects, gdjs.TutorialCode.mapOfGDgdjs_9546TutorialCode_9546GDPuertaObjects1Objects, false, runtimeScene, false);
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_Meta", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).add(runtimeScene.getGame().getVariables().getFromIndex(1).getAsNumber());
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


{


let isConditionTrue_0 = false;
{
gdjs.copyArray(runtimeScene.getObjects("HUD_Almas"), gdjs.TutorialCode.GDHUD_9595AlmasObjects1);
gdjs.copyArray(runtimeScene.getObjects("HUD_Vidas"), gdjs.TutorialCode.GDHUD_9595VidasObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595AlmasObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595AlmasObjects1[i].setString("ALMAS " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(1))) + " · VIDA +" + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(3))) + "/10");
}
}
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595VidasObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595VidasObjects1[i].setString("VIDAS");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Controles"), gdjs.TutorialCode.GDHUD_9595ControlesObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595ControlesObjects1[i].setString("←/→ MOVER · ESPACIO SALTAR · ESC PAUSA");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Controles"), gdjs.TutorialCode.GDHUD_9595ControlesObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595ControlesObjects1[i].setString("←/→ MOVER · ESPACIO SALTAR · X DASH · ESC PAUSA");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Controles"), gdjs.TutorialCode.GDHUD_9595ControlesObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595ControlesObjects1[i].setString("←/→ MOVER · ESPACIO SALTAR · J/CLIC ATACAR · ESC PAUSA");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(1)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Controles"), gdjs.TutorialCode.GDHUD_9595ControlesObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595ControlesObjects1[i].setString("←/→ MOVER · ESPACIO SALTAR · J/CLIC ATACAR · X DASH · ESC PAUSA");
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("HUD_Corazon"), gdjs.TutorialCode.GDHUD_9595CorazonObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariableNumber(gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariables().getFromIndex(0)) <= gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(0)) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDHUD_9595CorazonObjects1[k] = gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDHUD_9595CorazonObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].setAnimation(0);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("HUD_Corazon"), gdjs.TutorialCode.GDHUD_9595CorazonObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariableNumber(gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariables().getFromIndex(0)) > gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(0)) ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDHUD_9595CorazonObjects1[k] = gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length = k;
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDHUD_9595CorazonObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].setAnimation(1);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("HUD_Corazon"), gdjs.TutorialCode.GDHUD_9595CorazonObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariableNumber(gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].getVariables().getFromIndex(0)) == 1 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDHUD_9595CorazonObjects1[k] = gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(0).getAsNumber() > 0);
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(20).getAsNumber() > 0);
}
}
}
if (isConditionTrue_0) {
/* Reuse gdjs.TutorialCode.GDHUD_9595CorazonObjects1 */
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595CorazonObjects1[i].setAnimation(2);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_IconoDash"), gdjs.TutorialCode.GDHUD_9595IconoDashObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595IconoDashObjects1[i].setOpacity(80);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_IconoDash"), gdjs.TutorialCode.GDHUD_9595IconoDashObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595IconoDashObjects1[i].setOpacity(190);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_IconoDash"), gdjs.TutorialCode.GDHUD_9595IconoDashObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595IconoDashObjects1[i].setOpacity(125);
}
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Jugador"), gdjs.TutorialCode.GDJugadorObjects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(2)) > 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(3)) == 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
if (isConditionTrue_0) {
isConditionTrue_0 = false;
for (var i = 0, k = 0, l = gdjs.TutorialCode.GDJugadorObjects1.length;i<l;++i) {
    if ( gdjs.TutorialCode.GDJugadorObjects1[i].getVariableNumber(gdjs.TutorialCode.GDJugadorObjects1[i].getVariables().getFromIndex(5)) <= 0 ) {
        isConditionTrue_0 = true;
        gdjs.TutorialCode.GDJugadorObjects1[k] = gdjs.TutorialCode.GDJugadorObjects1[i];
        ++k;
    }
}
gdjs.TutorialCode.GDJugadorObjects1.length = k;
}
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_IconoDash"), gdjs.TutorialCode.GDHUD_9595IconoDashObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595IconoDashObjects1[i].setOpacity(255);
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.getTimerElapsedTimeInSecondsOrNaN(runtimeScene, "HUDNotice") >= 3.2;
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("HUD_Aviso"), gdjs.TutorialCode.GDHUD_9595AvisoObjects1);
{for(var i = 0, len = gdjs.TutorialCode.GDHUD_9595AvisoObjects1.length ;i < len;++i) {
    gdjs.TutorialCode.GDHUD_9595AvisoObjects1[i].setString("");
}
}
{gdjs.evtTools.runtimeScene.removeTimer(runtimeScene, "HUDNotice");
}
}

}


};

gdjs.TutorialCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.TutorialCode.GDFondoObjects1.length = 0;
gdjs.TutorialCode.GDFondoObjects2.length = 0;
gdjs.TutorialCode.GDFondoObjects3.length = 0;
gdjs.TutorialCode.GDSolidoObjects1.length = 0;
gdjs.TutorialCode.GDSolidoObjects2.length = 0;
gdjs.TutorialCode.GDSolidoObjects3.length = 0;
gdjs.TutorialCode.GDJugadorObjects1.length = 0;
gdjs.TutorialCode.GDJugadorObjects2.length = 0;
gdjs.TutorialCode.GDJugadorObjects3.length = 0;
gdjs.TutorialCode.GDPuertaObjects1.length = 0;
gdjs.TutorialCode.GDPuertaObjects2.length = 0;
gdjs.TutorialCode.GDPuertaObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects3.length = 0;
gdjs.TutorialCode.GDJefeObjects1.length = 0;
gdjs.TutorialCode.GDJefeObjects2.length = 0;
gdjs.TutorialCode.GDJefeObjects3.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects1.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects2.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects3.length = 0;
gdjs.TutorialCode.GDOndaDerObjects1.length = 0;
gdjs.TutorialCode.GDOndaDerObjects2.length = 0;
gdjs.TutorialCode.GDOndaDerObjects3.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects1.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects2.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects3.length = 0;
gdjs.TutorialCode.GDAlmaObjects1.length = 0;
gdjs.TutorialCode.GDAlmaObjects2.length = 0;
gdjs.TutorialCode.GDAlmaObjects3.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects1.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects2.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects3.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects1.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects2.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects3.length = 0;

gdjs.TutorialCode.eventsList6(runtimeScene);
gdjs.TutorialCode.GDFondoObjects1.length = 0;
gdjs.TutorialCode.GDFondoObjects2.length = 0;
gdjs.TutorialCode.GDFondoObjects3.length = 0;
gdjs.TutorialCode.GDSolidoObjects1.length = 0;
gdjs.TutorialCode.GDSolidoObjects2.length = 0;
gdjs.TutorialCode.GDSolidoObjects3.length = 0;
gdjs.TutorialCode.GDJugadorObjects1.length = 0;
gdjs.TutorialCode.GDJugadorObjects2.length = 0;
gdjs.TutorialCode.GDJugadorObjects3.length = 0;
gdjs.TutorialCode.GDPuertaObjects1.length = 0;
gdjs.TutorialCode.GDPuertaObjects2.length = 0;
gdjs.TutorialCode.GDPuertaObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595BarraObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595NivelObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595AlmasObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595VidasObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595AvisoObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595ControlesObjects3.length = 0;
gdjs.TutorialCode.GDJefeObjects1.length = 0;
gdjs.TutorialCode.GDJefeObjects2.length = 0;
gdjs.TutorialCode.GDJefeObjects3.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects1.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects2.length = 0;
gdjs.TutorialCode.GDOndaIzqObjects3.length = 0;
gdjs.TutorialCode.GDOndaDerObjects1.length = 0;
gdjs.TutorialCode.GDOndaDerObjects2.length = 0;
gdjs.TutorialCode.GDOndaDerObjects3.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects1.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects2.length = 0;
gdjs.TutorialCode.GDGolpePalaObjects3.length = 0;
gdjs.TutorialCode.GDAlmaObjects1.length = 0;
gdjs.TutorialCode.GDAlmaObjects2.length = 0;
gdjs.TutorialCode.GDAlmaObjects3.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects1.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects2.length = 0;
gdjs.TutorialCode.GDFarolCheckpointObjects3.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects1.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects2.length = 0;
gdjs.TutorialCode.GDPalaRecogibleObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoAlmaObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595IconoDashObjects3.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects1.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects2.length = 0;
gdjs.TutorialCode.GDHUD_9595CorazonObjects3.length = 0;


return;

}

gdjs['TutorialCode'] = gdjs.TutorialCode;
