"""Tests for Web Storage API features.

Tests features: namevalue-storage, indexeddb, indexeddb2,
                filereader, fileapi, bloburls, atob-btoa, textencoder
"""

import pytest


class TestNameValueStorage:
    """Tests for localStorage/sessionStorage detection."""

    def test_localstorage_set(self, parse_and_check):
        """Test localStorage.setItem()."""
        js = "localStorage.setItem('key', 'value');"
        assert parse_and_check(js, 'namevalue-storage')

    def test_localstorage_get(self, parse_and_check):
        """Test localStorage.getItem()."""
        js = "const value = localStorage.getItem('key');"
        assert parse_and_check(js, 'namevalue-storage')

    def test_sessionstorage_set(self, parse_and_check):
        """Test sessionStorage.setItem()."""
        js = "sessionStorage.setItem('session', 'data');"
        assert parse_and_check(js, 'namevalue-storage')

    def test_sessionstorage_get(self, parse_and_check):
        """Test sessionStorage.getItem()."""
        js = "const data = sessionStorage.getItem('session');"
        assert parse_and_check(js, 'namevalue-storage')

    def test_localstorage_clear(self, parse_and_check):
        """Test localStorage.clear()."""
        js = "localStorage.clear();"
        assert parse_and_check(js, 'namevalue-storage')


class TestIndexedDB:
    """Tests for IndexedDB detection."""

    def test_indexeddb_open(self, parse_and_check):
        """Test indexedDB.open()."""
        js = "const request = indexedDB.open('myDatabase', 1);"
        assert parse_and_check(js, 'indexeddb')

    def test_indexeddb_usage(self, parse_and_check):
        """Test IndexedDB usage pattern."""
        js = """
        const request = indexedDB.open('myDB', 1);
        request.onsuccess = e => {
            const db = e.target.result;
        };
        """
        assert parse_and_check(js, 'indexeddb')


class TestIndexedDB2:
    """Tests for IndexedDB 2.0 detection."""

    def test_idb_key_range(self, parse_and_check):
        """Test IDBKeyRange."""
        js = "const range = IDBKeyRange.bound(1, 100);"
        assert parse_and_check(js, 'indexeddb2')


class TestFileReader:
    """Tests for FileReader detection."""

    def test_new_file_reader(self, parse_and_check):
        """Test new FileReader."""
        js = "const reader = new FileReader();"
        assert parse_and_check(js, 'filereader')

    def test_file_reader_read(self, parse_and_check):
        """Test FileReader read methods."""
        js = """
        const reader = new FileReader();
        reader.onload = e => console.log(e.target.result);
        reader.readAsText(file);
        """
        assert parse_and_check(js, 'filereader')


class TestFileAPI:
    """Tests for File API detection."""

    def test_new_file(self, parse_and_check):
        """Test new File."""
        js = "const file = new File(['content'], 'filename.txt');"
        assert parse_and_check(js, 'fileapi')

    def test_new_blob(self, parse_and_check):
        """Test new Blob."""
        js = "const blob = new Blob(['data'], { type: 'text/plain' });"
        assert parse_and_check(js, 'fileapi')


class TestBlobURLs:
    """Tests for Blob URLs detection.

    Note: Pattern looks for createObjectURL specifically.
    """

    def test_create_object_url(self, parse_and_check):
        """Test URL.createObjectURL()."""
        js = "const url = URL.createObjectURL(blob);"
        assert parse_and_check(js, 'bloburls')

    def test_create_object_url_call(self, parse_and_check):
        """Test createObjectURL function call."""
        js = "const blobUrl = createObjectURL(file);"
        assert parse_and_check(js, 'bloburls')


class TestAtobBtoa:
    """Tests for Base64 encoding/decoding detection."""

    def test_btoa(self, parse_and_check):
        """Test btoa()."""
        js = "const encoded = btoa('Hello World');"
        assert parse_and_check(js, 'atob-btoa')

    def test_atob(self, parse_and_check):
        """Test atob()."""
        js = "const decoded = atob('SGVsbG8=');"
        assert parse_and_check(js, 'atob-btoa')


class TestTextEncoder:
    """Tests for TextEncoder/TextDecoder detection."""

    def test_new_text_encoder(self, parse_and_check):
        """Test new TextEncoder."""
        js = "const encoder = new TextEncoder();"
        assert parse_and_check(js, 'textencoder')

    def test_new_text_decoder(self, parse_and_check):
        """Test new TextDecoder."""
        js = "const decoder = new TextDecoder('utf-8');"
        assert parse_and_check(js, 'textencoder')

    def test_text_encoder_encode(self, parse_and_check):
        """Test TextEncoder.encode()."""
        js = """
        const encoder = new TextEncoder();
        const encoded = encoder.encode('Hello');
        """
        assert parse_and_check(js, 'textencoder')


class TestTypedArrays:
    """Tests for Typed Arrays detection."""

    def test_uint8array(self, parse_and_check):
        """Test Uint8Array."""
        js = "const arr = new Uint8Array(buffer);"
        assert parse_and_check(js, 'typedarrays')

    def test_arraybuffer(self, parse_and_check):
        """Test ArrayBuffer."""
        js = "const buffer = new ArrayBuffer(16);"
        assert parse_and_check(js, 'typedarrays')

    def test_dataview(self, parse_and_check):
        """Test DataView."""
        js = "const view = new DataView(buffer);"
        assert parse_and_check(js, 'typedarrays')


class TestSharedArrayBuffer:
    """Tests for SharedArrayBuffer detection."""

    def test_shared_array_buffer(self, parse_and_check):
        """Test SharedArrayBuffer."""
        js = "const sab = new SharedArrayBuffer(1024);"
        assert parse_and_check(js, 'sharedarraybuffer')

    def test_atomics(self, parse_and_check):
        """Test Atomics."""
        js = "Atomics.wait(int32Array, 0, 0);"
        assert parse_and_check(js, 'sharedarraybuffer')


class TestJSON:
    """Tests for JSON detection."""

    def test_json_parse(self, parse_and_check):
        """Test JSON.parse()."""
        js = "const obj = JSON.parse(jsonStr);"
        assert parse_and_check(js, 'json')

    def test_json_stringify(self, parse_and_check):
        """Test JSON.stringify()."""
        js = "const str = JSON.stringify({ key: 'value' });"
        assert parse_and_check(js, 'json')
