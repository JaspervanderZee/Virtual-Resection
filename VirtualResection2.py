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
    kidneyLabelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    kidneyLabelmapNode.SetName('Kidney labelmap for Virtual Resection')
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, kidneyLabelmapNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Kidney model for Virtual Resection")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, exportFolderItemId)
    modelNode = slicer.util.getNode('Kidney')
    modelNode.SetName('Kidney model for Virtual Resection')
  



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
    displayNode.SetSelectedColor([0.33333333333, 0.0, 1.0])
    displayNode.SetGlyphScale(1.5)
    displayNode.SetGlyphSize(8)
    displayNode.SetHandlesInteractive(False)
    displayNode.SetPointLabelsVisibility(False)
    displayNode.SetTextScale(0)
    
    markup_1.GetDisplayNode().SetVisibility(False)
    markup_2.GetDisplayNode().SetVisibility(False)

    
    
def CompleteResection():
    #Completes a segmentation of the Kidney labelmap to extract both the RRP and the Resected Volume.
        
    #Take the Kidney labelmap as volume to be segmented
    masterVolumeNode = slicer.util.getNode("Kidney labelmap for Virtual Resection")
    
    # Create sesgmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)
    
    
    #Create RRP and Resected Volume node and set colours
    addedSegmentID_RRP = segmentationNode.GetSegmentation().AddEmptySegment("RRP")
    segmentation = segmentationNode.GetSegmentation()
    segment=segmentation.GetSegment(segmentation.GetNthSegmentID(0))
    segment.SetColor(0.8666,0.5098,0.3961)
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
    segmentationNode.CreateClosedSurfaceRepresentation()
     
    # Thresholding of RRP
    segmentEditorNode.SetSelectedSegmentID(addedSegmentID_RRP)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","1")
    effect.setParameter("MaximumThreshold","2")
    effect.self().onApply()
    segmentationNode.CreateClosedSurfaceRepresentation()

    modelNode = slicer.util.getNode('Kidney model for Virtual Resection')
    modelNode.GetDisplayNode().SetVisibility(False)
    segmentationNode = slicer.util.getNode("Kidney")
    #segmentationNode.GetDisplayNode().SetVisibility(False)
    
    markupNode = slicer.util.getNode('Resection Points')
    markupNode.GetDisplayNode().SetVisibility(False)
    
    segmentationNode = slicer.util.getNode("Kidney") 
    segmentationNode.GetDisplayNode().SetVisibility(False)    

            
def Get_Statistics():
    #Quickly gives an overview of the Virtual Resection statistics.
    
    segmentationNode = slicer.util.getNode("Kidney")
    segmentationNode.SetName("Kidney_seg")
    segmentationNode = slicer.util.getNode("Kidney_seg")
    masterVolumeNode = slicer.util.getNode("Kidney labelmap for Virtual Resection")
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)
    segmentationNode2 = slicer.util.getNode("Segmentation")

    

    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segment_1", segmentationNode.GetID())
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()
    volume_Preoperative_Kidney = stats['Kidney',"LabelmapSegmentStatisticsPlugin.volume_cm3"]  
        
    segStatLogic2 = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic2.getParameterNode().SetParameter("Segmentation", segmentationNode2.GetID())
    segStatLogic2.computeStatistics()
    stats2 = segStatLogic2.getStatistics()

    volume_RRP = stats2['RRP',"LabelmapSegmentStatisticsPlugin.volume_cm3"]
    volume_resected = stats2['Resected Volume',"LabelmapSegmentStatisticsPlugin.volume_cm3"]
    percentage = (volume_RRP/volume_Preoperative_Kidney)*100
    
    
    print(f" Volume Preoperative Kidney  = {volume_Preoperative_Kidney} mL")
    print(f" Volume Postoperative Kidney  = {volume_RRP} mL")
    print(f" Volume Resected  = {volume_resected} mL")
    print(f" This is an percentage of = {percentage} %")
    
  
    
    
    
    