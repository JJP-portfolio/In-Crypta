gdjs.DerrotaCode = {};
gdjs.DerrotaCode.localVariables = [];
gdjs.DerrotaCode.idToCallbackMap = new Map();
gdjs.DerrotaCode.GDFondoDerrotaObjects1= [];
gdjs.DerrotaCode.GDFondoDerrotaObjects2= [];
gdjs.DerrotaCode.GDFondoDerrotaObjects3= [];
gdjs.DerrotaCode.GDDerrota_9595TituloObjects1= [];
gdjs.DerrotaCode.GDDerrota_9595TituloObjects2= [];
gdjs.DerrotaCode.GDDerrota_9595TituloObjects3= [];
gdjs.DerrotaCode.GDDerrota_9595CausaObjects1= [];
gdjs.DerrotaCode.GDDerrota_9595CausaObjects2= [];
gdjs.DerrotaCode.GDDerrota_9595CausaObjects3= [];
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1= [];
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects2= [];
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects3= [];
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1= [];
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects2= [];
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects3= [];
gdjs.DerrotaCode.GDDerrota_9595PromptObjects1= [];
gdjs.DerrotaCode.GDDerrota_9595PromptObjects2= [];
gdjs.DerrotaCode.GDDerrota_9595PromptObjects3= [];


gdjs.DerrotaCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 0);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Tutorial", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 1);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 2);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 3);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 3", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 11);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 12);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 13);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 3", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 14);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 4", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 15);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 5", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getGame().getVariables().getFromIndex(8).getAsNumber() == 16);
}
if (isConditionTrue_0) {
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 6", false);
}
}

}


};gdjs.DerrotaCode.eventsList1 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Derrota_Stat1"), gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Derrota_Stat2"), gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1);
{runtimeScene.getGame().getVariables().getFromIndex(11).setNumber(512);
}
{runtimeScene.getGame().getVariables().getFromIndex(12).setNumber(288);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1.25, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 512, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 288, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 640, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 360, "UI", 0);
}
{for(var i = 0, len = gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1.length ;i < len;++i) {
    gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1[i].setString("CAÍDAS TOTALES: " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(6))));
}
}
{for(var i = 0, len = gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1.length ;i < len;++i) {
    gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1[i].setString("ALMAS COSECHADAS: " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(2))));
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(0);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}

{ //Subevents
gdjs.DerrotaCode.eventsList0(runtimeScene);} //End of subevents
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Escape");
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", false);
}
}

}


};

gdjs.DerrotaCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.DerrotaCode.GDFondoDerrotaObjects1.length = 0;
gdjs.DerrotaCode.GDFondoDerrotaObjects2.length = 0;
gdjs.DerrotaCode.GDFondoDerrotaObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects3.length = 0;

gdjs.DerrotaCode.eventsList1(runtimeScene);
gdjs.DerrotaCode.GDFondoDerrotaObjects1.length = 0;
gdjs.DerrotaCode.GDFondoDerrotaObjects2.length = 0;
gdjs.DerrotaCode.GDFondoDerrotaObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595TituloObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595CausaObjects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat1Objects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595Stat2Objects3.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects1.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects2.length = 0;
gdjs.DerrotaCode.GDDerrota_9595PromptObjects3.length = 0;


return;

}

gdjs['DerrotaCode'] = gdjs.DerrotaCode;
