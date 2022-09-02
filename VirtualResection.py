#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 10:59:00 2022

@author: myrthebuser
"""
import slicer



def Init():
    #Initialises the Virtual Resection process by creating a kidney model and a kidney labelmap, both needed in the following steps.
    
    segmentationNode = slicer.util.getNode("Kidney")
    segmentationNode_copy = slicer.util.getNode("Kidney")
    kidneyLabelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    kidneyLabelmapNode.SetName('Kidney labelmap')
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, kidneyLabelmapNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Kidney-model")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, exportFolderItemId)
    



def MergePoints():
    #Merges Closed Curve points and Fiducial Points to one list of Fiducial points in the format needed for the ResectionVolume module.
    
    markup_1=slicer.util.getNode('CC')
    markup_2=slicer.util.getNode('F')
    fiducialNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    fiducialNode.SetName('Resection Points')
    slicer.util.updateMarkupsControlPointsFromArray(fiducialNode, slicer.util.arrayFromMarkupsControlPoints(markup_1))
    
    
    arr=slicer.util.arrayFromMarkupsControlPoints(markup_2)
    for i in arr:           
     slicer.modules.markups.logic().AddControlPoint(i[0], i[1], i[2])
     
    markupNode = slicer.util.getNode('Resection Points')
    displayNode = markupNode.GetDisplayNode()
    displayNode.SetSelectedColor([0.95,0.60,0.2])
    displayNode.SetGlyphScale(4)
    displayNode.SetTextScale(0)

    
    
def CompleteResection():
    #Completes a segmentation of the Kidney labelmap to extract both the RRP and the Resected Volume.
        
    #Take the Kidney labelmap as volume to be segmented
    masterVolumeNode = slicer.util.getNode("Kidney labelmap")
    
    # Create sesgmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)
    
    
    #Create RRP and Resected Volume node and set colours
    addedSegmentID_RRP = segmentationNode.GetSegmentation().AddEmptySegment("RRP")
    segmentation = segmentationNode.GetSegmentation()
    segment=segmentation.GetSegment(segmentation.GetNthSegmentID(0))
    segment.SetColor(0.99,0.6,0.0)
    addedSegmentID_resected = segmentationNode.GetSegmentation().AddEmptySegment("Resected Volume")
    segment=segmentation.GetSegment(segmentation.GetNthSegmentID(1))
    segment.SetColor(0.7,0.0,0.9)
    
    
    # Create segment editor to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)
    
    # Thresholding of Resected Volume
    segmentEditorNode.SetSelectedSegmentID(addedSegmentID_resected)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","2.9")
    effect.setParameter("MaximumThreshold","3.5")
    effect.self().onApply()
    
    
    
    # Thresholding of RRP
    segmentEditorNode.SetSelectedSegmentID(addedSegmentID_RRP)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","1")
    effect.setParameter("MaximumThreshold","2")
    effect.self().onApply()
            
def get_statistics():
    #Quickly gives an overview of the Virtual Resection statistics.
    
    segmentationNode = slicer.util.getNode("Segmentation")
    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()



    volume_RRP = stats['RRP',"LabelmapSegmentStatisticsPlugin.volume_cm3"]
    volume_resected = stats['Resected Volume',"LabelmapSegmentStatisticsPlugin.volume_cm3"]
    percentage = (volume_RRP/volume_resected)*100
    
    
    print(f" Volume Remaining  = {volume_RRP} mL")
    print(f" Volume Resected  = {volume_resected} mL")
    print(f" This is an percentage of = {percentage} %")
    
  
    
    
    
    