import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { PlusCircleIcon } from "@heroicons/react/24/outline";
import CourseCard from "../components/CourseCard";
import { listAvailableCourses } from "../redux/slice/courseSlice";

const Courses = () => {
  const dispatch = useDispatch();
  const courses = useSelector((state) => state.course.courses);

  useEffect(() => {
    dispatch(listAvailableCourses());
  }, []);

  const handleAddCourseClick = () => {
    // dispatch(insertCourse({ course: { name: "testInsert", private: false, description: "this is a test thingy!" } }));
  };

  return (
    <div className="container">
      <div className="flex w-full items-center justify-between">
        <h1 className="text-6xl font-extrabold">My Courses</h1>
        <div className="flex items-center space-x-2">
          <Link to={"/create-course"}>
            <button
              className="btn-primary mt-4 inline-flex items-center rounded-full"
            >
              <PlusCircleIcon className="mr-2 h-8 w-8" />
              <span>Create Course</span>
            </button>
          </Link>
          <button
            className="btn-primary mt-4 inline-flex items-center rounded-full"
            onClick={handleAddCourseClick}
          >
            <PlusCircleIcon className="mr-2 h-8 w-8" />
            <span>Add Course</span>
          </button>
        </div>
      </div>
      <div className="grid grid-flow-row grid-cols-3 gap-4 py-8">
        {courses.length > 0
          ? courses.map((course, index) => {
              return (
                <CourseCard
                  key={index}
                  title={course.name}
                  description={course.description}
                />
              );
            })
          : null}
      </div>
    </div>
  );
};

export default Courses;
