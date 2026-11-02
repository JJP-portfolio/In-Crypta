gdjs.VictoriaCode = {};
gdjs.VictoriaCode.localVariables = [];
gdjs.VictoriaCode.idToCallbackMap = new Map();
gdjs.VictoriaCode.GDFondoVictoriaObjects1= [];
gdjs.VictoriaCode.GDFondoVictoriaObjects2= [];
gdjs.VictoriaCode.GDVictoria_9595TituloObjects1= [];
gdjs.VictoriaCode.GDVictoria_9595TituloObjects2= [];
gdjs.VictoriaCode.GDVictoria_9595StatsObjects1= [];
gdjs.VictoriaCode.GDVictoria_9595StatsObjects2= [];
gdjs.VictoriaCode.GDVictoria_9595PromptObjects1= [];
gdjs.VictoriaCode.GDVictoria_9595PromptObjects2= [];


gdjs.VictoriaCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Victoria_Stats"), gdjs.VictoriaCode.GDVictoria_9595StatsObjects1);
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
{for(var i = 0, len = gdjs.VictoriaCode.GDVictoria_9595StatsObjects1.length ;i < len;++i) {
    gdjs.VictoriaCode.GDVictoria_9595StatsObjects1[i].setString("ALMAS RECOLECTADAS: " + gdjs.evtTools.common.toString(gdjs.evtTools.variable.getVariableNumber(runtimeScene.getGame().getVariables().getFromIndex(2))));
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
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

gdjs.VictoriaCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.VictoriaCode.GDFondoVictoriaObjects1.length = 0;
gdjs.VictoriaCode.GDFondoVictoriaObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595TituloObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595TituloObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595StatsObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595StatsObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595PromptObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595PromptObjects2.length = 0;

gdjs.VictoriaCode.eventsList0(runtimeScene);
gdjs.VictoriaCode.GDFondoVictoriaObjects1.length = 0;
gdjs.VictoriaCode.GDFondoVictoriaObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595TituloObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595TituloObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595StatsObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595StatsObjects2.length = 0;
gdjs.VictoriaCode.GDVictoria_9595PromptObjects1.length = 0;
gdjs.VictoriaCode.GDVictoria_9595PromptObjects2.length = 0;


return;

}

gdjs['VictoriaCode'] = gdjs.VictoriaCode;
