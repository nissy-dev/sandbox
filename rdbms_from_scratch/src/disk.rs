use std::{
    // convert::TryInto,
    fs::{File, OpenOptions},
    io::{self, Read, Seek, SeekFrom, Write},
    path::Path,
    u64,
};

// use zerocopy::{AsBytes, FromBytes};

pub const PAGE_SIZE: usize = 4096;
#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash)]
#[repr(C)]
pub struct PageId(pub u64);
impl PageId {
    pub const INVALID_PAGE_ID: PageId = PageId(u64::MAX);

    pub fn valid(self) -> Option<PageId> {
        if self == Self::INVALID_PAGE_ID {
            None
        } else {
            Some(self)
        }
    }

    pub fn to_u64(self) -> u64 {
        self.0
    }
}

// impl Default for PageId {
//     fn default() -> Self {
//         Self::INVALID_PAGE_ID
//     }
// }

// impl From<Option<PageId>> for PageId {
//     fn from(page_id: Option<PageId>) -> Self {
//         page_id.unwrap_or_default()
//     }
// }

// impl From<&[u8]> for PageId {
//     fn from(bytes: &[u8]) -> Self {
//         let arr = bytes.try_into().unwrap();
//         PageId(u64::from_ne_bytes(arr))
//     }
// }

pub struct DiskManager {
    heap_file: File,
    next_page_id: u64,
}

impl DiskManager {
    pub fn new(heap_file: File) -> io::Result<Self> {
        let heap_file_size = heap_file.metadata()?.len();
        let next_page_id = heap_file_size / PAGE_SIZE as u64;
        Ok(Self {
            heap_file,
            next_page_id,
        })
    }

    pub fn open(heap_file_path: impl AsRef<Path>) -> io::Result<Self> {
        let heap_file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(heap_file_path)?; // ? = エラーが帰ったら早期リターン
        Self::new(heap_file)
    }

    pub fn allocate_page(&mut self) -> PageId {
        let page_id = self.next_page_id;
        self.next_page_id += 1;
        PageId(page_id)
    }

    pub fn read_page_data(&mut self, page_id: PageId, data: &mut [u8]) -> io::Result<()> {
        let offset = PAGE_SIZE as u64 * page_id.to_u64();
        self.heap_file.seek(SeekFrom::Start(offset))?;
        self.heap_file.read_exact(data)
    }

    pub fn write_page_data(&mut self, page_id: PageId, data: &[u8]) -> io::Result<()> {
        let offset = PAGE_SIZE as u64 * page_id.to_u64();
        self.heap_file.seek(SeekFrom::Start(offset))?;
        self.heap_file.write_all(data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test() {
        // ディスクマネージャーの作成
        let (data_file, data_file_path) = NamedTempFile::new().unwrap().into_parts();
        let mut disk = DiskManager::new(data_file).unwrap();

        // データの書き込み
        let mut hello = Vec::with_capacity(PAGE_SIZE);
        hello.extend_from_slice(b"hello");
        hello.resize(PAGE_SIZE, 0);
        let hello_page_id = disk.allocate_page();
        println!("hello_page_id: {:?}", hello_page_id);
        disk.write_page_data(hello_page_id, &hello).unwrap();

        // データの書き込み
        let mut world = Vec::with_capacity(PAGE_SIZE);
        world.extend_from_slice(b"world");
        world.resize(PAGE_SIZE, 0);
        let world_page_id = disk.allocate_page();
        println!("hello_page_id: {:?}", world_page_id);
        disk.write_page_data(world_page_id, &world).unwrap();

        // ディスクマネージャーの削除
        drop(disk);

        // 新しいディスクマネージャーの作成
        let mut disk2 = DiskManager::open(&data_file_path).unwrap();

        // データの読み込み
        let mut buf = vec![0; PAGE_SIZE];
        disk2.read_page_data(hello_page_id, &mut buf).unwrap();
        assert_eq!(hello, buf);

        // データの読み込み
        disk2.read_page_data(world_page_id, &mut buf).unwrap();
        assert_eq!(world, buf);
    }
}
