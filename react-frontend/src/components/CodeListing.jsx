import React, { useEffect, useState, useRef, createRef } from "react";
import CodeView from "./CodeView";
import DropDown from "./DropDown";
import Code from "./Code";
import {
  disassembleBinary,
  decompileFunction,
} from "../redux/slice/codeListingSlice";
import { useSelector, useDispatch } from "react-redux";

const CodeListing = () => {
  const dispatch = useDispatch();
  const fileInfo = useSelector((state) => state.codeListing.fileInfo);
  const functions = useSelector((state) => state.codeListing.functions);
  const exports = useSelector((state) => state.codeListing.exports);
  const imports = useSelector((state) => state.codeListing.imports);
  const sections = useSelector((state) => state.codeListing.sections);
  const classes = useSelector((state) => state.codeListing.classes);
  // const entry = useSelector((state) => state.codeListing.entry);
  const symbols = useSelector((state) => state.codeListing.symbols);
  const strings = useSelector((state) => state.codeListing.strings);
  const assembly = useSelector((state) => state.codeListing.assembly);
  const topAddress = useSelector((state) => state.codeListing.topAddress);
  const bottomAddress = useSelector((state) => state.codeListing.bottomAddress);
  const decompiledCode = useSelector(
    (state) => state.codeListing.decompiledCode,
  );
  const currentFilePath = useSelector((state) => state.sandbox.currentFilePath);

  const [scrollTop, setScrollTop] = useState(null);
  const [scrollBot, setScrollBot] = useState(null);
  const [oldAssemblyHeight, setOldAssemblyHeight] = useState(0);
  const [highlight, setHighlight] = useState("");
  const [noAssemblyScroll, setNoAssemblyScroll] = useState(true);
  const assemblyContainerRef = useRef(null);
  const assemblyListRef = useRef(null);

  const handleAssemblyScroll = (event) => {
    setScrollTop(event.currentTarget.scrollTop);
    setScrollBot(
      event.currentTarget.scrollHeight -
        (event.currentTarget.scrollTop + event.currentTarget.clientHeight),
    );
  };

  useEffect(() => {
    return () => {
      if (assemblyContainerRef.current) {
        assemblyContainerRef.current.scrollTo(0, 0);
      }
    };
  }, []);

  useEffect(() => {
    if (oldAssemblyHeight === 0 || scrollTop !== 0) return;
    if (oldAssemblyHeight !== assemblyListRef.current.clientHeight) {
      assemblyContainerRef.current.scrollTo({
        top: assemblyListRef.current.clientHeight - oldAssemblyHeight,
        behavior: "instant",
      });
    }
  }, [assembly, scrollTop]);

  useEffect(() => {
    if (scrollTop === null || scrollBot === null) return;
    if (noAssemblyScroll) {
      setNoAssemblyScroll(false);
      return;
    }
    if (scrollTop === 0) {
      setOldAssemblyHeight(assemblyListRef.current.clientHeight);
      dispatch(
        disassembleBinary({
          filename: currentFilePath,
          direction: "up",
          target: `${topAddress}`,
          mode: "concat",
        }),
      );
    }
    if (scrollBot === 0) {
      dispatch(
        disassembleBinary({
          filename: currentFilePath,
          direction: "down",
          target: `${bottomAddress}`,
          mode: "concat",
        }),
      );
    }
  }, [scrollTop, scrollBot]);

  const handleMetadataClick = (e, address, type) => {
    setHighlight(address);
    setNoAssemblyScroll(true);
    setOldAssemblyHeight(0);
    dispatch(
      disassembleBinary({
        filename: currentFilePath,
        direction: null,
        target: address,
        mode: "refresh",
      }),
    );
    if (type !== "string") {
      dispatch(
        decompileFunction({
          filename: currentFilePath,
          address: address,
        }),
      );
    }
    assemblyContainerRef.current.scrollTo({
      top: 0,
      behavior: "instant",
    });
  };

  const handleAssemblyClick = (address) => {
    setHighlight(address);
    dispatch(
      decompileFunction({
        filename: currentFilePath,
        address: "0x" + address.toString(16),
      }),
    );
  };

  const handleDecompiledCodeClick = (address) => {
    setHighlight(address);
  };

  return (
    <>
      <div className="justify-ceter mt-2 flex max-h-[calc(100vh_-_10rem)] flex-1 space-x-4 p-4">
        <div className="flex max-w-xs flex-1 flex-col">
          <h1 className="w-full text-center">MetaData</h1>
          <div className="h-full w-full overflow-y-scroll">
            <DropDown
              className="mt-2 w-full"
              label="File Info"
              items={fileInfo}
              type="fileInfo"
            />
            <DropDown
              className="mt-2 w-full"
              label="Sections"
              items={sections}
              type="sections"
              handleClick={handleMetadataClick}
            />
            <DropDown
              className="mt-2 w-full"
              label="Functions"
              items={functions}
              type="functions"
              handleClick={handleMetadataClick}
            />
            <DropDown
              className="mt-2 w-full"
              label="Exports"
              items={exports}
              type="exports"
              handleClick={handleMetadataClick}
            />
            <DropDown
              className="mt-2 w-full"
              label="Imports"
              items={imports}
              type="imports"
              handleClick={handleMetadataClick}
            />
            <DropDown
              className="mt-2 w-full"
              label="Classes"
              items={classes}
              type="classes"
            />
            <DropDown
              className="mt-2 w-full"
              label="Symbols"
              items={symbols}
              type="symbols"
              handleClick={handleMetadataClick}
            />
            <DropDown
              className="mt-2 w-full"
              label="Strings"
              items={strings}
              type="strings"
              handleClick={handleMetadataClick}
            />
          </div>
        </div>
        <div className="flex flex-1 flex-col overflow-hidden">
          <h1 className="w-full text-center">Assembly</h1>
          <CodeView
            className="mt-2 flex flex-1 flex-col overflow-scroll whitespace-pre text-left font-mono"
            onScroll={handleAssemblyScroll}
            ref={assemblyContainerRef}
          >
            <div className="w-full" id="assemblyList">
              <ul ref={assemblyListRef} className="w-fit">
                {assembly
                  ? assembly.map((line, index) => {
                      let isHighlighted =
                        line.offset === highlight ? true : false;
                      return (
                        <li
                          key={index}
                          onClick={() => handleAssemblyClick(line.offset)}
                          className={`${
                            isHighlighted ? "bg-ctp-overlay0" : null
                          } w-full`}
                        >
                          <Code language="x86asm">{line.text}</Code>
                        </li>
                      );
                    })
                  : null}
              </ul>
            </div>
          </CodeView>
        </div>
        <div className="flex flex-1 flex-col overflow-hidden">
          <h1 className="w-full text-center">Decompiled C Code</h1>
          <CodeView className="mt-2 h-full w-full overflow-scroll whitespace-pre text-left font-mono">
            <div className="w-full">
              <ul>
                {decompiledCode
                  ? decompiledCode.map((line, index) => {
                      let isHighlighted =
                        line.address === highlight && line.address !== null
                          ? true
                          : false;
                      return (
                        <li
                          key={index}
                          onClick={() =>
                            handleDecompiledCodeClick(line.address)
                          }
                          className={`${
                            isHighlighted ? "bg-ctp-overlay0" : null
                          } w-full`}
                        >
                          <Code language="c">{line.code}</Code>
                        </li>
                      );
                    })
                  : null}
              </ul>
            </div>
          </CodeView>
        </div>
      </div>
    </>
  );
};

export default CodeListing;
