#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 10:59:00 2022

@author: myrthebuser
"""
import slicer

def merge():
    markup_1=slicer.util.getNode('CC')
    markup_2=slicer.util.getNode('F')
    fiducialNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    slicer.util.updateMarkupsControlPointsFromArray(fiducialNode, slicer.util.arrayFromMarkupsControlPoints(markup_1))
    
    
    arr=slicer.util.arrayFromMarkupsControlPoints(markup_2)
    for i in arr:           
     slicer.modules.markups.logic().AddControlPoint(i[0], i[1], i[2])
     
    markupNode = slicer.util.getNode('MarkupsFiducial')
    displayNode = markupNode.GetDisplayNode()
    displayNode.SetSelectedColor([0.95,0.60,0.2])
    displayNode.SetGlyphScale(8)
    displayNode.SetTextScale(0)

def init():
    segmentationNode = slicer.util.getNode("Kidney")
    segmentationNode_copy = slicer.util.getNode("Kidney")
    kidneyLabelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    kidneyLabelmapNode_copy = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    kidneyLabelmapNode.SetName('Kidney labelmap')
    kidneyLabelmapNode_copy.SetName('Copy of kidney labelmap')
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, kidneyLabelmapNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode_copy, kidneyLabelmapNode_copy, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)

    
    segmentationNode = slicer.util.getNode("Tumor")
    tumorLabelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    tumorLabelmapNode.SetName('Tumor labelmap')
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, tumorLabelmapNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)