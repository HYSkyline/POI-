Attribute VB_Name = "ģ��2"
Option Explicit

Sub reformat()
'����csv��, ȥ�����ڵ�ַ�к��ж��Ŷ������Ĵ�������
'��Ҫ�ֶ��޸ĵ�һ��Forѭ�����ж�λ��Ϊ��ַ������
'����������һ�еĺ�һ��
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
