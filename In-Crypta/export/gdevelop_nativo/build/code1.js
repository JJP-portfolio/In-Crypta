gdjs.PausaCode = {};
gdjs.PausaCode.localVariables = [];
gdjs.PausaCode.idToCallbackMap = new Map();
gdjs.PausaCode.GDFondoPausaObjects1= [];
gdjs.PausaCode.GDFondoPausaObjects2= [];
gdjs.PausaCode.GDPausa_9595TituloObjects1= [];
gdjs.PausaCode.GDPausa_9595TituloObjects2= [];
gdjs.PausaCode.GDPausa_9595SubObjects1= [];
gdjs.PausaCode.GDPausa_9595SubObjects2= [];
gdjs.PausaCode.GDPausa_9595Opcion1Objects1= [];
gdjs.PausaCode.GDPausa_9595Opcion1Objects2= [];
gdjs.PausaCode.GDPausa_9595Opcion2Objects1= [];
gdjs.PausaCode.GDPausa_9595Opcion2Objects2= [];
gdjs.PausaCode.GDPausa_9595Opcion3Objects1= [];
gdjs.PausaCode.GDPausa_9595Opcion3Objects2= [];
gdjs.PausaCode.GDPausa_9595AyudaObjects1= [];
gdjs.PausaCode.GDPausa_9595AyudaObjects2= [];


gdjs.PausaCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
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
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion1"), gdjs.PausaCode.GDPausa_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion2"), gdjs.PausaCode.GDPausa_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion3"), gdjs.PausaCode.GDPausa_9595Opcion3Objects1);
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion1Objects1[i].setString(">> CONTINUAR <<");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion2Objects1[i].setString("REINICIAR NIVEL");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion3Objects1[i].setString("VOLVER AL TÍTULO");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion1"), gdjs.PausaCode.GDPausa_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion2"), gdjs.PausaCode.GDPausa_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion3"), gdjs.PausaCode.GDPausa_9595Opcion3Objects1);
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion1Objects1[i].setString("CONTINUAR");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion2Objects1[i].setString(">> REINICIAR NIVEL <<");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion3Objects1[i].setString("VOLVER AL TÍTULO");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion1"), gdjs.PausaCode.GDPausa_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion2"), gdjs.PausaCode.GDPausa_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Pausa_Opcion3"), gdjs.PausaCode.GDPausa_9595Opcion3Objects1);
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion1Objects1[i].setString("CONTINUAR");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion2Objects1[i].setString("REINICIAR NIVEL");
}
}
{for(var i = 0, len = gdjs.PausaCode.GDPausa_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.PausaCode.GDPausa_9595Opcion3Objects1[i].setString(">> VOLVER AL TÍTULO <<");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(3);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() > 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).sub(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() < 3);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).add(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.popScene(runtimeScene);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(1);
}
{gdjs.evtTools.runtimeScene.popScene(runtimeScene);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", true);
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
{gdjs.evtTools.runtimeScene.popScene(runtimeScene);
}
}

}


};

gdjs.PausaCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.PausaCode.GDFondoPausaObjects1.length = 0;
gdjs.PausaCode.GDFondoPausaObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595TituloObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595TituloObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595SubObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595SubObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion1Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion1Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion2Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion2Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion3Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion3Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595AyudaObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595AyudaObjects2.length = 0;

gdjs.PausaCode.eventsList0(runtimeScene);
gdjs.PausaCode.GDFondoPausaObjects1.length = 0;
gdjs.PausaCode.GDFondoPausaObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595TituloObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595TituloObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595SubObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595SubObjects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion1Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion1Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion2Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion2Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion3Objects1.length = 0;
gdjs.PausaCode.GDPausa_9595Opcion3Objects2.length = 0;
gdjs.PausaCode.GDPausa_9595AyudaObjects1.length = 0;
gdjs.PausaCode.GDPausa_9595AyudaObjects2.length = 0;


return;

}

gdjs['PausaCode'] = gdjs.PausaCode;
