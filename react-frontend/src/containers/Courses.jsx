import React from "react";

import { PlusCircleIcon } from "@heroicons/react/24/outline";

import CourseCard from "../components/CourseCard";

const Courses = () => {
  return (
    <div className="container">
      <div className="flex w-full items-center justify-between">
        <h1 className="text-6xl font-extrabold">My Courses</h1>
        <button className="btn-primary mt-4 inline-flex items-center rounded-full">
          <PlusCircleIcon className="mr-2 h-8 w-8" />
          <span>Add Course</span>
        </button>
      </div>
      <div className="grid grid-flow-row grid-cols-3 gap-4 py-8">
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
      </div>
    </div>
  );
};

export default Courses;
