extern crate getopts;
extern crate brotli;
extern crate base64;

use getopts::{Options};
use std::env;
use std::io;
use std::io::Write;


fn main() {
    let args: Vec<String> = env::args().collect();

    let opts = Options::new();
    let matches = match opts.parse(&args[1..]) {
        Ok(m) => { m }
        Err(f) => { panic!(f.to_string()) }
    };
    let input = if !matches.free.is_empty() {
        matches.free[0].clone()
    } else {
        return;
    };

    let mut vec: Vec<u8> = vec![];
    {
        let mut writer = brotli::CompressorWriter::new(&mut vec, 4096, 5, 20);
        writer.write(&input.as_bytes()).unwrap();
    }

    let encoded = base64::encode(&vec);
    print!("{}", encoded);
}