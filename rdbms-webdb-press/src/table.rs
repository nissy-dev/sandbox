use anyhow::Result;

use crate::btree::BTree;
use crate::buffer::BufferPoolManager;
use crate::disk::PageId;
use crate::tuple;

#[derive(Debug)]
pub struct SimpleTable {
    pub meta_page_id: PageId, // テーブルの内容が入っているB+TreeのメタページのID
    pub num_key_elems: usize, // 主キーの位置
}

impl SimpleTable {
    pub fn create(&mut self, bufmgr: &mut BufferPoolManager) -> Result<()> {
        let btree = BTree::create(bufmgr)?;
        self.meta_page_id = btree.meta_page_id;
        Ok(())
    }

    pub fn insert(&self, bufmgr: &mut BufferPoolManager, record: &[&[u8]]) -> Result<()> {
        let btree = BTree::new(self.meta_page_id);
        let mut key = vec![];
        tuple::encode(record[..self.num_key_elems].iter(), &mut key);
        let mut value = vec![];
        tuple::encode(record[self.num_key_elems..].iter(), &mut value);
        // 木を構築するのと同時に、BufferPoolManagerのメソッドを内部で呼んで、ページの読み書きしている
        btree.insert(bufmgr, &key, &value)?;
        Ok(())
    }
}

// セカンダリインデックス用のテーブル
#[derive(Debug)]
pub struct UniqueIndex {
    pub meta_page_id: PageId, // セカンダリインデックス用のテーブルの内容が入っているB+TreeのメタページのID
    pub skey: Vec<usize>,     // セカンダリキーに含める列を指定するフィールド
}

impl UniqueIndex {
    pub fn create(&mut self, bufmgr: &mut BufferPoolManager) -> Result<()> {
        let btree = BTree::create(bufmgr)?;
        self.meta_page_id = btree.meta_page_id;
        Ok(())
    }

    pub fn insert(
        &self,
        bufmgr: &mut BufferPoolManager,
        pkey: &[u8],
        record: &[impl AsRef<[u8]>],
    ) -> Result<()> {
        let btree = BTree::new(self.meta_page_id);
        let mut skey = vec![];

        // セカンダリキーのエンコード
        tuple::encode(
            self.skey.iter().map(|&index| record[index].as_ref()),
            &mut skey,
        );
        btree.insert(bufmgr, &skey, pkey)?;
        Ok(())
    }
}

#[derive(Debug)]
pub struct Table {
    pub meta_page_id: PageId, // テーブルの内容が入っているB+TreeのメタページのID
    pub num_key_elems: usize, // 主キーの位置
    pub unique_indices: Vec<UniqueIndex>,
}

impl Table {
    pub fn create(&mut self, bufmgr: &mut BufferPoolManager) -> Result<()> {
        let btree = BTree::create(bufmgr)?;
        self.meta_page_id = btree.meta_page_id;
        for unique_index in &mut self.unique_indices {
            unique_index.create(bufmgr)?;
        }
        Ok(())
    }

    pub fn insert(&self, bufmgr: &mut BufferPoolManager, record: &[&[u8]]) -> Result<()> {
        let btree = BTree::new(self.meta_page_id);
        let mut key = vec![];
        tuple::encode(record[..self.num_key_elems].iter(), &mut key);
        let mut value = vec![];
        tuple::encode(record[self.num_key_elems..].iter(), &mut value);
        // 木を構築するのと同時に、BufferPoolManagerのメソッドを内部で呼んで、ページの読み書きしている
        btree.insert(bufmgr, &key, &value)?;

        for unique_index in &self.unique_indices {
            unique_index.insert(bufmgr, &key, record)?;
        }
        Ok(())
    }
}
