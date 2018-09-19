Attribute VB_Name = "模块2"
Option Explicit

Sub reformat()
'导入csv后, 去除由于地址中含有逗号而产生的串行现象
'需要手动修改第一处For循环的判定位置为地址所在列
'光标置于最后一列的后一列
Dim ecount As Integer
Dim i As Integer
Dim adt As String

Do Until ActiveCell.Offset(0, -14).Value = ""
    ecount = 0
    Do Until ActiveCell.Offset(0, ecount).Value = ""
        ecount = ecount + 1
    Loop
    If ecount > 0 Then
        adt = ""
        For i = 0 To ecount
            If adt = "" Then
                adt = CStr(ActiveCell.Offset(0, -10 + i).Value)
            Else
                adt = adt + ", " + CStr(ActiveCell.Offset(0, -10 + i).Value)
            End If
        Next i
        ActiveCell.Offset(0, -10).FormulaR1C1 = adt
        For i = -9 To ecount - 1
            ActiveCell.Offset(0, i).FormulaR1C1 = ActiveCell.Offset(0, i + ecount).Value
        Next i
    End If
    ActiveCell.Offset(1, 0).Range("a1").Select
Loop
End Sub
