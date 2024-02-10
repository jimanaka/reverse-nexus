import React from "react";
import { useEffect } from "react";
import { Tab } from "@headlessui/react";

import CodeListing from "../components/CodeListing";
import Debugger from "../components/Debugger";
import PayloadGenerator from "../components/PayloadGenerator";

import { setCurrentTab } from "../redux/slice/sandboxSlice";
import { initSocket, disconnect } from "../redux/slice/sessionSlice";
import { useDispatch, useSelector } from "react-redux";

const Sandbox = () => {
  const dispatch = useDispatch();
  const currentTab = useSelector((state) => state.sandbox.currentTab);
  const isConnected = useSelector((state) => state.session.isConnected);
  const gdbPID = useSelector((state) => state.session.gdbPID);

  useEffect(() => {
    if (!isConnected) {
      dispatch(initSocket());
    }

    return () => {
      if (isConnected) {
        console.log("disconnecting socket");
        dispatch(disconnect(gdbPID));
      }
    };
  }, [isConnected]);

  const handleTabChange = (index) => {
    dispatch(setCurrentTab(index));
  };

  let component = null;
  switch (currentTab) {
    case 0:
      component = <CodeListing classname="w-full"/>;
      break;
    case 1:
      component = <Debugger classname="w-full"/>;
      break;
    case 2:
      component = <PayloadGenerator classname="w-full"/>;
      break;
    default:
      component = null;
  }

  return (
    <>
      <div className="bg-ctp-mantle w-full space-x-4 py-4 pl-8">
        <Tab.Group onChange={(index) => handleTabChange(index)}>
          <Tab.List className="flex justify-center">
            <Tab className="flex-1">Listing</Tab>
            <Tab className="flex-1">Debugger</Tab>
            <Tab className="flex-1">Payload Generator</Tab>
          </Tab.List>
        </Tab.Group>
      </div>
      {component}
    </>
  );
};

export default Sandbox;
