// Function: nvo_md5.of_md5()
//--------------------------------------------------------------------
// Description: Calculate the MD5 message digest hash of a string Using the Windows Crypto API ( PB 10 later)
//--------------------------------------------------------------------
// Arguments:
// 	value	blob	abl_text
//--------------------------------------------------------------------
// Returns:  string
//--------------------------------------------------------------------
// Author:	PB.BaoGa		Date: 2022/01/09
//--------------------------------------------------------------------
// Usage: nvo_md5.of_md5 ( blob abl_text )
//--------------------------------------------------------------------
//	Copyright (c) PB.BaoGa(TM), All rights reserved.
//--------------------------------------------------------------------
// Modify History:
//
//====================================================================

ULong MD5LEN = 16
ULong hProv // provider handle
ULong hHash // hash object handle
ULong err_number
String ls_result, ls_null
Integer i, l, r, b
Blob{16} bl_hash
Blob{1} bl_byte

SetNull (ls_null)
ULong cbHash = 0
Char HexDigits[0 To 15] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'}

//Get handle to the crypto provider
If Not CryptAcquireContextA(hProv, ls_null, ls_null, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT) Then
	err_number = GetLastError()
	Return 'acquire context failed ' + String (err_number)
End If

// Create the hash object
If Not CryptCreateHash(hProv, CALG_MD5, 0, 0, hHash) Then
	err_number = GetLastError()
	CryptReleaseContext(hProv, 0)
	Return 'create hash failed ' + String (err_number)
End If

// Add the input to the hash
If Not CryptHashData(hHash, abl_text, Len(abl_text), 0) Then
	err_number = GetLastError()
	CryptDestroyHash(hHash)
	CryptReleaseContext(hProv, 0)
	Return 'hashdata failed ' + String (err_number)
End If

// Get the hash value and convert it to readable characters
cbHash = MD5LEN
If (CryptGetHashParam(hHash, HP_HASHVAL, bl_hash, cbHash, 0)) Then
	For i = 1 To 16
		bl_byte = BlobMid (bl_hash, i, 1)
		b = AscA(String(bl_byte,EncodingANSI!))
		r = Mod (b, 16) // right 4 bits
		l = b / 16 // left 4 bits
		ls_result += HexDigits [l] + HexDigits [r]
	Next
Else
	err_number = GetLastError()
	Return 'gethashparam failed ' + String (err_number)
End If

// clean up and return
CryptDestroyHash(hHash)
CryptReleaseContext(hProv, 0)

Return ls_result