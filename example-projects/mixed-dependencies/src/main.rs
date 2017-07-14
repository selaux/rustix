extern crate brotli;
extern crate base64;

use std::env;
use std::io::Write;


fn main() {
    let args: Vec<String> = env::args().collect();

    let input = if !args.is_empty() {
        args[1].clone()
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