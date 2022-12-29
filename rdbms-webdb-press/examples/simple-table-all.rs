use anyhow::Result;

use rdbms_from_scratch::btree::{BTree, SearchMode};
use rdbms_from_scratch::buffer::{BufferPool, BufferPoolManager};
use rdbms_from_scratch::disk::{DiskManager, PageId};
use rdbms_from_scratch::tuple;

fn main() -> Result<()> {
    let disk = DiskManager::open("simple.rly")?;
    let pool = BufferPool::new(10);
    let mut bufmgr = BufferPoolManager::new(disk, pool);

    let btree = BTree::new(PageId(0));
    let mut iter = btree.search(&mut bufmgr, SearchMode::Start)?;

    while let Some((key, value)) = iter.next(&mut bufmgr)? {
        let mut record = vec![];
        tuple::decode(&key, &mut record);
        tuple::decode(&value, &mut record);
        println!("{:?}", tuple::Pretty(&record));
    }
    Ok(())
}
